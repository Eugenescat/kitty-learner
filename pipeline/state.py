"""Shared state shape for the LangGraph pipeline."""

from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    """State passed between pipeline nodes."""
    file_id: str
    title: str
    pdf_path: str
    paper_text: str
    paper_summary: str
    paper_topics: Any
    topics_data: dict[str, Any]
    posts_data: list[dict[str, Any]]
    topic_count: int
    post_count: int
    errors: list[str]
    metrics: dict[str, Any]


def build_initial_state(file_id: str, title: str, pdf_path: str) -> PipelineState:
    """Create an initial pipeline state for a PDF processing run."""
    return {
        "file_id": file_id,
        "title": title,
        "pdf_path": pdf_path,
        "errors": [],
        "metrics": {},
    }

