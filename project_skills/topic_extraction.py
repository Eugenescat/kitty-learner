"""Skill wrapper for topic extraction."""

from pydantic import BaseModel

from topic_extractor import PaperTopics, extract_topics

from .base import Skill


class TopicExtractionInput(BaseModel):
    paper_text: str


class TopicExtractionSkill(Skill):
    name = "topic_extraction"
    input_schema = TopicExtractionInput

    def run(self, **kwargs) -> PaperTopics:
        data = self.input_schema(**kwargs)
        return extract_topics(data.paper_text)

