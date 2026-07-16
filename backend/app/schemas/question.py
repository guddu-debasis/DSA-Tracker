from pydantic import BaseModel


class QuestionOut(BaseModel):
    id: str
    category: str
    title: str
    url: str | None = None
    order: int
    solved: bool = False


class CategoryGroup(BaseModel):
    category: str
    total: int
    solved: int
    questions: list[QuestionOut]


class ProgressToggleRequest(BaseModel):
    solved: bool


class ProgressSummary(BaseModel):
    total_questions: int
    total_solved: int
    by_category: list[dict]
