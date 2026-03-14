"""Central registry for project skills."""

from .base import Skill
from .feed_storage import FeedStorageSkill
from .post_generation import PostGenerationSkill
from .topic_extraction import TopicExtractionSkill

_SKILLS: dict[str, Skill] = {
    "topic_extraction": TopicExtractionSkill(),
    "post_generation": PostGenerationSkill(),
    "feed_storage": FeedStorageSkill(),
}


def get_skill(name: str) -> Skill:
    """Fetch a skill instance by name."""
    if name not in _SKILLS:
        raise KeyError(f"Unknown skill: {name}")
    return _SKILLS[name]

