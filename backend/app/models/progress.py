from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class Progress(Document):
    user_id: str
    question_id: str
    solved: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "progress"
        indexes = [
            IndexModel(
                [("user_id", ASCENDING), ("question_id", ASCENDING)],
                unique=True,
                name="user_question_unique",
            )
        ]
