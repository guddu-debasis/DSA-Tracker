from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from app.core.deps import get_current_user
from app.models.progress import Progress
from app.models.question import Question
from app.models.user import User
from app.schemas.question import ProgressToggleRequest

router = APIRouter(prefix="/progress", tags=["progress"])


@router.put("/{question_id}")
async def set_progress(
    question_id: str,
    payload: ProgressToggleRequest,
    user: User = Depends(get_current_user),
):
    question = await Question.get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    existing = await Progress.find_one(
        Progress.user_id == str(user.id), Progress.question_id == question_id
    )
    if existing:
        existing.solved = payload.solved
        existing.updated_at = datetime.now(timezone.utc)
        await existing.save()
    else:
        existing = Progress(
            user_id=str(user.id),
            question_id=question_id,
            solved=payload.solved,
        )
        await existing.insert()

    return {"question_id": question_id, "solved": existing.solved}
