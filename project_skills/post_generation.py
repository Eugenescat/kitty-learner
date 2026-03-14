"""Skill wrapper for post generation."""

from pydantic import BaseModel

from generator import Post, generate_all_posts
from topic_extractor import PaperTopics

from .base import Skill


class PostGenerationInput(BaseModel):
    paper_topics: PaperTopics
    agents_per_topic: int = 2
    replies_per_post: int = 1

    model_config = {"arbitrary_types_allowed": True}


class PostGenerationSkill(Skill):
    name = "post_generation"
    input_schema = PostGenerationInput

    def run(self, **kwargs) -> list[Post]:
        data = self.input_schema(**kwargs)
        return generate_all_posts(
            data.paper_topics,
            agents_per_topic=data.agents_per_topic,
            replies_per_post=data.replies_per_post,
        )

