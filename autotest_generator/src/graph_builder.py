"""Functions related to the creation of a graph based on predefined nodes and
edges."""

from typing import Optional

from langgraph.graph import END, StateGraph

from .node import (GraphState, analyze_function, finalize_file,
                   generate_single_test, plan_tests, prepare_iteration,
                   should_continue_generating)


def build_workflow_graph(save_image_path: Optional[str] = None):
    """Builds the workflow graph for the autotest generator.

    Args:
        save_image_path: Optional path to save the graph image.

    Returns:
        The compiled workflow graph.
    """
    workflow = StateGraph(GraphState)
    workflow.add_node("analyze_function", analyze_function)
    workflow.add_node("plan_tests", plan_tests)
    workflow.add_node("prepare_iteration", prepare_iteration)
    workflow.add_node("generate_single_test", generate_single_test)
    workflow.add_node("finalize_file", finalize_file)

    workflow.set_entry_point("analyze_function")
    workflow.add_edge("analyze_function", "plan_tests")
    workflow.add_edge("plan_tests", "prepare_iteration")

    workflow.add_conditional_edges(
        "prepare_iteration",
        should_continue_generating,
        {
            "continue_generation": "generate_single_test",
            "finalize": "finalize_file",
        },
    )

    workflow.add_conditional_edges(
        "generate_single_test",
        should_continue_generating,
        {
            "continue_generation": "generate_single_test",
            "finalize": "finalize_file",
        },
    )
    workflow.add_edge("finalize_file", END)

    graph = workflow.compile()

    # Save the graph image if requested
    if save_image_path is not None:
        png_bytes = graph.get_graph().draw_mermaid_png()
        with open(save_image_path, "wb") as file:
            file.write(png_bytes)

    return graph
