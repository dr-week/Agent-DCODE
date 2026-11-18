"""
Composable StateGraph engine (LangGraph-style DAG / cyclical state machine).
Allows connecting custom nodes and conditional edges for any workflow.
"""

from typing import Any, Callable, Dict, Optional

END = "__END__"
StateDict = Dict[str, Any]
NodeFn = Callable[[StateDict], StateDict]
RouterFn = Callable[[StateDict], str]


class StateGraph:
    """Deterministic state machine supporting linear and conditional agent transitions."""

    def __init__(self, entry_point: str = "start"):
        self.entry_point = entry_point
        self.nodes: Dict[str, NodeFn] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, RouterFn] = {}

    def add_node(self, name: str, fn: NodeFn) -> "StateGraph":
        self.nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        self.edges[source] = target
        return self

    def add_conditional_edges(self, source: str, router: RouterFn) -> "StateGraph":
        self.conditional_edges[source] = router
        return self

    def run(self, initial_state: Optional[StateDict] = None, max_steps: int = 25) -> StateDict:
        state: StateDict = dict(initial_state or {})
        state.setdefault("_trace", [])
        current = self.entry_point
        steps = 0

        while current != END and steps < max_steps:
            steps += 1
            node_fn = self.nodes.get(current)
            if not node_fn:
                raise ValueError(f"StateGraph node '{current}' is not registered.")

            state["_trace"].append(current)
            state = node_fn(state)

            if current in self.conditional_edges:
                current = self.conditional_edges[current](state)
            elif current in self.edges:
                current = self.edges[current]
            else:
                current = END

        state["_steps_executed"] = steps
        return state
