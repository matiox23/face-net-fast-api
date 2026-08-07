from fastapi import APIRouter, Depends, HTTPException, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep, require_roles
from src.app.modules.exam.service.exam_exceptions import ExamNotFoundError
from src.app.modules.exam_attempt.dto.exam_attempt_dto import (
    AttemptQuestionListResponse,
    ExamAttemptResponse,
)
from src.app.modules.exam_attempt.model.exam_attempt_model import ExamAttempt
from src.app.modules.exam_attempt.service.exam_attempt_exceptions import (
    AttemptAlreadyExistsError,
    AttemptNotInProgressError,
    ExamAttemptNotFoundError,
    ExamNotPublishedError,
)
from src.app.modules.exam_attempt.service.exam_attempt_service import ExamAttemptService

router = APIRouter(prefix="/exams/{exam_id}/attempts", tags=["exam-attempts"])


async def _ensure_attempt_owner(
    exam_id: int, attempt_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamAttempt:
    try:
        attempt = await ExamAttemptService(session).get_attempt_entity(attempt_id)
    except ExamAttemptNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if attempt.exam_id != exam_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attempt does not belong to this exam")
    if attempt.student_id != current.user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    return attempt


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("STUDENT"))])
async def start_attempt(
    exam_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamAttemptResponse:
    try:
        return await ExamAttemptService(session).start_attempt(exam_id, current.user.id)
    except ExamNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ExamNotPublishedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except AttemptAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/{attempt_id}")
async def get_attempt(
    exam_id: int, attempt_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamAttemptResponse:
    await _ensure_attempt_owner(exam_id, attempt_id, session, current)
    return await ExamAttemptService(session).get_attempt(attempt_id)


@router.get("/{attempt_id}/questions")
async def get_attempt_questions(
    exam_id: int, attempt_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> AttemptQuestionListResponse:
    await _ensure_attempt_owner(exam_id, attempt_id, session, current)
    return await ExamAttemptService(session).get_questions_for_attempt(exam_id)


@router.post("/{attempt_id}/submit")
async def submit_attempt(
    exam_id: int, attempt_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamAttemptResponse:
    await _ensure_attempt_owner(exam_id, attempt_id, session, current)
    try:
        return await ExamAttemptService(session).submit_attempt(attempt_id)
    except AttemptNotInProgressError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
