"""
LangGraph-specific callback handler for Lunary.
Captures graph structure, execution flow, and detailed metadata.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import traceback

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
    from langchain_core.agents import AgentFinish
    from langchain_core.documents import Document
    from langchain_core.messages import BaseMessage
except ImportError:
    BaseCallbackHandler = object
    
from . import LunaryCallbackHandler, track_event, run_manager
from .config import get_config
from .utils import create_uuid_from_string

logger = logging.getLogger(__name__)


class LangGraphCallbackHandler(LunaryCallbackHandler):
    """
    Enhanced callback handler for LangGraph execution tracking.
    Captures graph structure, execution flow, and detailed metadata.
    """
    
    def __init__(
        self,
        app_id: Union[str, None] = None,
        api_url: Union[str, None] = None,
        graph_mode: bool = True,
        capture_graph_structure: bool = True,
        **kwargs
    ):
        """
        Initialize the LangGraph callback handler.
        
        Args:
            app_id: Lunary application ID
            api_url: Lunary API URL
            graph_mode: Enable graph-specific tracking
            capture_graph_structure: Capture and send graph structure data
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(app_id=app_id, api_url=api_url, **kwargs)
        
        self.graph_mode = graph_mode
        self.capture_graph_structure = capture_graph_structure
        
        # Graph metadata tracking
        self.graph_metadata = {
            "nodes": {},
            "edges": [],
            "execution_order": [],
            "node_types": {},
            "supersteps": [],
            "parallel_executions": {},
            "conditional_evaluations": []
        }
        
        # Execution state tracking
        self._current_step = 0
        self._node_execution_counts = {}
        self._execution_path = []
        self._parallel_branches = {}
        self._graph_run_id = None
        
    def _is_langgraph_execution(self, serialized: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Detect if this is a LangGraph execution."""
        if not metadata:
            return False
            
        # Check for LangGraph-specific metadata
        langgraph_indicators = [
            "langgraph_node",
            "langgraph_step", 
            "langgraph_triggers",
            "langgraph_path",
            "langgraph_checkpoint_ns"
        ]
        
        has_langgraph_metadata = any(key in metadata for key in langgraph_indicators)
        
        # Check serialized name
        is_langgraph_name = serialized and serialized.get("name") == "LangGraph"
        
        return has_langgraph_metadata or is_langgraph_name
        
    def _determine_node_type(self, metadata: Dict[str, Any], serialized: Dict[str, Any] = None) -> str:
        """Determine the type of graph node."""
        node_name = metadata.get("langgraph_node", "")
        
        # Check metadata hints
        if "agent" in node_name.lower():
            return "agent"
        elif "tool" in node_name.lower():
            return "tool"
        elif "condition" in node_name.lower() or "route" in node_name.lower():
            return "conditional"
        elif any(trigger.startswith("parallel") for trigger in metadata.get("langgraph_triggers", [])):
            return "parallel"
        
        # Check serialized data
        if serialized:
            if serialized.get("name") == "ToolNode":
                return "tool"
            elif "Agent" in serialized.get("name", ""):
                return "agent"
                
        return "chain"
        
    def _extract_node_name(self, metadata: Dict[str, Any], serialized: Dict[str, Any] = None) -> str:
        """Extract node name from various sources."""
        # First try metadata
        if metadata and "langgraph_node" in metadata:
            return metadata["langgraph_node"]
            
        # Then try serialized name
        if serialized and "name" in serialized:
            return serialized["name"]
            
        # Try to extract from path
        if metadata and "langgraph_path" in metadata:
            path = metadata["langgraph_path"]
            if isinstance(path, list) and len(path) > 1:
                return path[-1]
                
        return "unknown_node"
        
    def _track_graph_structure(self, run_id: str, metadata: Dict[str, Any], serialized: Dict[str, Any] = None):
        """Track and update graph structure based on execution."""
        node_name = self._extract_node_name(metadata, serialized)
        node_type = self._determine_node_type(metadata, serialized)
        
        # Update node registry
        if node_name not in self.graph_metadata["nodes"]:
            self.graph_metadata["nodes"][node_name] = {
                "id": node_name,
                "type": node_type,
                "execution_count": 0,
                "metadata": {
                    "first_seen_step": metadata.get("langgraph_step", self._current_step)
                }
            }
            
        # Update execution count
        self.graph_metadata["nodes"][node_name]["execution_count"] += 1
        
        # Track execution order
        self.graph_metadata["execution_order"].append({
            "node": node_name,
            "run_id": str(run_id),
            "step": metadata.get("langgraph_step", self._current_step),
            "timestamp": metadata.get("timestamp"),
            "triggers": metadata.get("langgraph_triggers", [])
        })
        
        # Infer edges from triggers
        triggers = metadata.get("langgraph_triggers", [])
        for trigger in triggers:
            if trigger.startswith("branch:to:"):
                source_node = self._get_previous_node()
                if source_node and source_node != node_name:
                    edge = {
                        "source": source_node,
                        "target": node_name,
                        "type": "sequential"
                    }
                    if edge not in self.graph_metadata["edges"]:
                        self.graph_metadata["edges"].append(edge)
                        
        # Track parallel executions
        if "parallel" in metadata.get("langgraph_triggers", []):
            branch_id = metadata.get("parallel_branch_id", str(run_id))
            if branch_id not in self._parallel_branches:
                self._parallel_branches[branch_id] = []
            self._parallel_branches[branch_id].append(node_name)
            
        # Update execution path
        self._execution_path.append(node_name)
        
    def _get_previous_node(self) -> Optional[str]:
        """Get the previous node in execution path."""
        if len(self._execution_path) > 0:
            return self._execution_path[-1]
        return None
        
    def _send_graph_event(self, event_type: str, run_id: str, data: Dict[str, Any]):
        """Send graph-specific events to Lunary."""
        if not self.graph_mode:
            return
            
        try:
            self._LunaryCallbackHandler__track_event(
                "graph",
                event_type,
                run_id=str(run_id),
                metadata={
                    "graph_data": data,
                    "graph_metadata": self.graph_metadata
                },
                app_id=self._LunaryCallbackHandler__app_id,
                api_url=self._LunaryCallbackHandler__api_url,
                callback_queue=self.queue,
                runtime="langgraph-py"
            )
        except Exception as e:
            logger.exception(f"Error sending graph event: {e}")
            
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Union[UUID, None] = None,
        tags: Union[List[str], None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        **kwargs: Any
    ) -> Any:
        """Enhanced chain start handler for LangGraph."""
        try:
            # Detect if this is the main graph execution starting
            if serialized and serialized.get("name") == "LangGraph" and not self._graph_run_id:
                self._graph_run_id = str(run_id)
                self._send_graph_event("graph_start", run_id, {
                    "inputs": inputs,
                    "tags": tags,
                    "metadata": metadata
                })
                
            # Check if this is a LangGraph node execution
            if self._is_langgraph_execution(serialized, metadata or {}):
                # Track graph structure
                self._track_graph_structure(run_id, metadata or {}, serialized)
                
                # Update current step
                if metadata and "langgraph_step" in metadata:
                    self._current_step = metadata["langgraph_step"]
                    
                # Send node start event
                node_name = self._extract_node_name(metadata or {}, serialized)
                self._send_graph_event("node_start", run_id, {
                    "node": node_name,
                    "step": self._current_step,
                    "metadata": metadata
                })
                
                # Check for conditional evaluation
                if "route" in node_name.lower() or "condition" in node_name.lower():
                    self.graph_metadata["conditional_evaluations"].append({
                        "node": node_name,
                        "step": self._current_step,
                        "run_id": str(run_id)
                    })
                    
        except Exception as e:
            logger.exception(f"Error in LangGraph on_chain_start: {e}")
            
        # Call parent implementation
        super().on_chain_start(
            serialized=serialized,
            inputs=inputs,
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata,
            **kwargs
        )
        
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Union[UUID, None] = None,
        **kwargs: Any
    ) -> Any:
        """Enhanced chain end handler for LangGraph."""
        try:
            # Check if this is the main graph execution ending
            if str(run_id) == self._graph_run_id:
                # Send final graph structure
                self._send_graph_event("graph_end", run_id, {
                    "outputs": outputs,
                    "graph_structure": self.graph_metadata,
                    "execution_summary": {
                        "total_nodes": len(self.graph_metadata["nodes"]),
                        "total_edges": len(self.graph_metadata["edges"]),
                        "total_steps": self._current_step,
                        "unique_nodes_executed": len(set(self._execution_path)),
                        "total_executions": len(self._execution_path)
                    }
                })
                
            # Send node end event
            run = run_manager.runs.get(str(run_id))
            if run and hasattr(run, 'metadata'):
                metadata = run.metadata
                if self._is_langgraph_execution({}, metadata):
                    node_name = self._extract_node_name(metadata)
                    self._send_graph_event("node_end", run_id, {
                        "node": node_name,
                        "outputs": outputs,
                        "metadata": metadata
                    })
                    
        except Exception as e:
            logger.exception(f"Error in LangGraph on_chain_end: {e}")
            
        # Call parent implementation
        super().on_chain_end(
            outputs=outputs,
            run_id=run_id,
            parent_run_id=parent_run_id,
            **kwargs
        )
        
    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Union[UUID, None] = None,
        **kwargs: Any
    ) -> Any:
        """Enhanced error handler for LangGraph."""
        try:
            # Send graph error event
            run = run_manager.runs.get(str(run_id))
            if run and hasattr(run, 'metadata'):
                metadata = run.metadata
                if self._is_langgraph_execution({}, metadata):
                    node_name = self._extract_node_name(metadata)
                    self._send_graph_event("node_error", run_id, {
                        "node": node_name,
                        "error": {
                            "message": str(error),
                            "type": type(error).__name__,
                            "stack": traceback.format_exc()
                        },
                        "metadata": metadata
                    })
                    
        except Exception as e:
            logger.exception(f"Error in LangGraph on_chain_error: {e}")
            
        # Call parent implementation
        super().on_chain_error(
            error=error,
            run_id=run_id,
            parent_run_id=parent_run_id,
            **kwargs
        )
        
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the captured graph structure."""
        return {
            "nodes": list(self.graph_metadata["nodes"].values()),
            "edges": self.graph_metadata["edges"],
            "execution_order": self.graph_metadata["execution_order"],
            "statistics": {
                "total_nodes": len(self.graph_metadata["nodes"]),
                "total_edges": len(self.graph_metadata["edges"]),
                "total_steps": self._current_step,
                "unique_nodes": len(set(self._execution_path)),
                "total_executions": len(self._execution_path),
                "has_cycles": self._detect_cycles(),
                "has_parallel": len(self._parallel_branches) > 0,
                "has_conditionals": len(self.graph_metadata["conditional_evaluations"]) > 0
            }
        }
        
    def _detect_cycles(self) -> bool:
        """Detect if the graph has cycles based on execution path."""
        visited = set()
        for node in self._execution_path:
            if node in visited:
                return True
            visited.add(node)
        return False
        
    def reset(self):
        """Reset the handler state for a new graph execution."""
        self.graph_metadata = {
            "nodes": {},
            "edges": [],
            "execution_order": [],
            "node_types": {},
            "supersteps": [],
            "parallel_executions": {},
            "conditional_evaluations": []
        }
        self._current_step = 0
        self._node_execution_counts = {}
        self._execution_path = []
        self._parallel_branches = {}
        self._graph_run_id = None