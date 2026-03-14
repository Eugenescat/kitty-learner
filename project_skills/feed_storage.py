"""Skill wrapper for feed persistence."""

from typing import Any

from pydantic import BaseModel

import database

from .base import Skill


class FeedStorageInput(BaseModel):
    file_id: str
    title: str
    summary: str
    topics_data: dict[str, Any]
    posts_data: list[dict[str, Any]]


class FeedStorageSkill(Skill):
    name = "feed_storage"
    input_schema = FeedStorageInput

    def run(self, **kwargs) -> None:
        data = self.input_schema(**kwargs)
        database.save_feed_with_fallback(
            file_id=data.file_id,
            title=data.title,
            summary=data.summary,
            topics_data=data.topics_data,
            posts_data=data.posts_data,
        )

