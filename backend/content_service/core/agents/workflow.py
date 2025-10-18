"""
LangGraph workflow with self-correction capability
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    agent_reasoning_node,
    tool_execution_node,
    quality_check_node,
    should_continue_after_execution,
    should_retry_after_quality_check,
)


def create_exam_evaluation_workflow():
    """
    Create the exam evaluation workflow with self-correction.

    Flow:
    1. reasoning → tool_execution
    2. tool_execution → quality_check (if evaluate task) OR end
    3. quality_check → retry (if issues found) OR end
    4. retry → back to reasoning (max 2-3 iterations)
    """

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("reasoning", agent_reasoning_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("quality_check", quality_check_node)

    # Set entry point
    workflow.set_entry_point("reasoning")

    # Edges
    workflow.add_edge("reasoning", "tool_execution")

    # Conditional edge after tool_execution
    workflow.add_conditional_edges(
        "tool_execution", should_continue_after_execution, {"quality_check": "quality_check", "end": END}
    )

    # Conditional edge after quality_check
    workflow.add_conditional_edges(
        "quality_check",
        should_retry_after_quality_check,
        {
            "retry": "reasoning",  # Loop back for retry
            "end": END,
        },
    )

    # Compile the graph
    return workflow.compile()


# Create singleton instance
exam_evaluation_graph = create_exam_evaluation_workflow()
