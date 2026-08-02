"""
LangGraph node implementations for FoundrAI workflow graphs.

Nodes are pure async callables:  async (state: WorkflowState) -> dict
Each node returns only the state keys it modifies.
"""
