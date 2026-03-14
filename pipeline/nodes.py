"""Pipeline node implementations."""

from pdf_parser import extract_text_from_pdf
from project_skills.registry import get_skill
from topic_extractor import Topic

from .state import PipelineState


def _post_to_dict(post) -> dict:
    """Convert a generated Post object to JSON-serializable dict."""
    topic: Topic | None = post.topic
    return {
        "id": post.id,
        "agent": {
            "nickname": post.agent.nickname,
            "name": post.agent.name,
            "avatar_emoji": post.agent.avatar_emoji,
        },
        "topic": {
            "topic_id": topic.topic_id,
            "title": topic.title,
            "core_idea": topic.core_idea,
            "why_it_matters": topic.why_it_matters,
            "controversy_level": topic.controversy_level,
            "source_section": topic.source_section,
            "difficulty": topic.difficulty,
        } if topic else None,
        "content": post.content,
        "likes": post.likes,
        "replies": [
            {
                "agent": {
                    "nickname": reply.agent.nickname,
                    "avatar_emoji": reply.agent.avatar_emoji,
                },
                "content": reply.content,
                "likes": reply.likes,
            }
            for reply in post.replies
        ],
    }


def extract_text_node(state: PipelineState) -> dict:
    """Extract plain text from uploaded PDF."""
    pdf_path = state.get("pdf_path")
    if not pdf_path:
        raise ValueError("Missing pdf_path in pipeline state")

    print(f"📄 Extracting text from {pdf_path}...")
    paper_text = extract_text_from_pdf(pdf_path)
    metrics = dict(state.get("metrics", {}))
    metrics["paper_text_chars"] = len(paper_text)
    return {"paper_text": paper_text, "metrics": metrics}


def extract_topics_node(state: PipelineState) -> dict:
    """Extract structured topics from paper text via skill."""
    paper_text = state.get("paper_text", "")
    if not paper_text:
        raise ValueError("No paper text available for topic extraction")

    print("🔍 Extracting topics...")
    skill = get_skill("topic_extraction")
    paper_topics = skill.run(paper_text=paper_text)

    topics_data = {
        "paper_summary": paper_topics.paper_summary,
        "topics": [
            {
                "topic_id": t.topic_id,
                "title": t.title,
                "core_idea": t.core_idea,
                "why_it_matters": t.why_it_matters,
                "controversy_level": t.controversy_level,
                "source_section": t.source_section,
                "difficulty": t.difficulty,
            }
            for t in paper_topics.topics
        ],
        "recommended_order": paper_topics.recommended_order,
    }

    metrics = dict(state.get("metrics", {}))
    metrics["topic_count"] = len(paper_topics.topics)
    return {
        "paper_topics": paper_topics,
        "paper_summary": paper_topics.paper_summary,
        "topics_data": topics_data,
        "topic_count": len(paper_topics.topics),
        "metrics": metrics,
    }


def generate_posts_node(state: PipelineState) -> dict:
    """Generate posts and replies from topics via skill."""
    paper_topics = state.get("paper_topics")
    if paper_topics is None:
        raise ValueError("No paper topics available for post generation")

    print("🤖 Generating posts...")
    skill = get_skill("post_generation")
    posts = skill.run(
        paper_topics=paper_topics,
        agents_per_topic=2,
        replies_per_post=1,
    )

    posts_data = [_post_to_dict(post) for post in posts]
    metrics = dict(state.get("metrics", {}))
    metrics["post_count"] = len(posts_data)
    return {
        "posts_data": posts_data,
        "post_count": len(posts_data),
        "metrics": metrics,
    }


def save_feed_node(state: PipelineState) -> dict:
    """Persist the generated feed via skill."""
    print("💾 Saving feed...")
    skill = get_skill("feed_storage")
    skill.run(
        file_id=state.get("file_id", ""),
        title=state.get("title", ""),
        summary=state.get("paper_summary", ""),
        topics_data=state.get("topics_data", {}),
        posts_data=state.get("posts_data", []),
    )
    return {}

