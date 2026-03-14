"""LangGraph orchestration for PDF processing pipeline."""

from langgraph.graph import END, START, StateGraph

from .nodes import (
    extract_text_node,
    extract_topics_node,
    generate_posts_node,
    save_feed_node,
)
from .state import PipelineState


def _build_graph():
    builder = StateGraph(PipelineState)
    builder.add_node("extract_text", extract_text_node)
    builder.add_node("extract_topics", extract_topics_node)
    builder.add_node("generate_posts", generate_posts_node)
    builder.add_node("save_feed", save_feed_node)

    builder.add_edge(START, "extract_text")
    builder.add_edge("extract_text", "extract_topics")
    builder.add_edge("extract_topics", "generate_posts")
    builder.add_edge("generate_posts", "save_feed")
    builder.add_edge("save_feed", END)
    return builder.compile()


_GRAPH = _build_graph()


def run_pipeline(initial_state: PipelineState) -> PipelineState:
    """Run full PDF processing pipeline and capture errors in state."""
    try:
        return _GRAPH.invoke(initial_state)
    except Exception as exc:
        errors = list(initial_state.get("errors", []))
        errors.append(str(exc))
        failed = dict(initial_state)
        failed["errors"] = errors
        return failed

