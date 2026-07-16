from collections import OrderedDict

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.question import Question
from app.models.progress import Progress
from app.models.user import User
from app.schemas.question import QuestionOut, CategoryGroup, ProgressSummary

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[CategoryGroup])
async def list_questions(user: User = Depends(get_current_user)):
    questions = await Question.find_all().sort("category", "order").to_list()
    progress_docs = await Progress.find(Progress.user_id == str(user.id)).to_list()
    solved_map = {p.question_id: p.solved for p in progress_docs}

    grouped: "OrderedDict[str, list[QuestionOut]]" = OrderedDict()
    for q in questions:
        qout = QuestionOut(
            id=str(q.id),
            category=q.category,
            title=q.title,
            url=q.url,
            order=q.order,
            solved=solved_map.get(str(q.id), False),
        )
        grouped.setdefault(q.category, []).append(qout)

    result = []
    for category, qlist in grouped.items():
        solved_count = sum(1 for q in qlist if q.solved)
        result.append(
            CategoryGroup(
                category=category,
                total=len(qlist),
                solved=solved_count,
                questions=qlist,
            )
        )
    return result


@router.get("/summary", response_model=ProgressSummary)
async def summary(user: User = Depends(get_current_user)):
    questions = await Question.find_all().to_list()
    progress_docs = await Progress.find(
        Progress.user_id == str(user.id), Progress.solved == True  # noqa: E712
    ).to_list()
    solved_ids = {p.question_id for p in progress_docs}

    by_category: dict[str, dict] = {}
    for q in questions:
        entry = by_category.setdefault(q.category, {"category": q.category, "total": 0, "solved": 0})
        entry["total"] += 1
        if str(q.id) in solved_ids:
            entry["solved"] += 1

    return ProgressSummary(
        total_questions=len(questions),
        total_solved=len(solved_ids),
        by_category=list(by_category.values()),
    )
