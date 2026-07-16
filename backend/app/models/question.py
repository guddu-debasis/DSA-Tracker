from beanie import Document, Indexed
from typing import Annotated


class Question(Document):
    category: Annotated[str, Indexed()]
    title: str
    url: str | None = None
    order: int = 0  # position within category, for stable ordering

    class Settings:
        name = "questions"
