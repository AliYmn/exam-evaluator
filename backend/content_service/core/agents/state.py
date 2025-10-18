"""
Agent state definition for LangGraph
"""

from typing import Dict, Any, List, TypedDict, Annotated
from operator import add


class AgentState(TypedDict):
    """
    State for the exam evaluation agent.
    This state is passed through all nodes in the graph.
    """

    # Input data
    task: str  # Current task: "parse_answer_key", "parse_student", "evaluate", "analyze"
    pdf_text: str  # PDF content to process
    context: Dict[str, Any]  # Additional context (answer key, student data, etc.)

    # Agent reasoning (accumulated across nodes)
    thoughts: Annotated[List[str], add]  # Agent's reasoning steps
    actions: Annotated[List[str], add]  # Actions taken
    observations: Annotated[List[str], add]  # Observations from actions

    # Tool outputs
    intermediate_results: Dict[str, Any]  # Results from tools

    # Quality control
    quality_checks: Annotated[List[Dict[str, Any]], add]  # Quality check results
    retry_count: int  # Number of retries attempted
    needs_review: bool  # Flag for human review (low confidence)

    # Final output
    final_output: Dict[str, Any]  # Final result
    status: str  # "processing", "completed", "failed", "needs_review"
    error: str  # Error message if failed

    # Metadata for tracking
    confidence_scores: List[float]  # Track confidence across evaluations
    tool_call_logs: Annotated[List[Dict[str, Any]], add]  # Log of all tool calls
