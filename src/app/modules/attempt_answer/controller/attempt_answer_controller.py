from fastapi import APIRouter, HTTPException, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.attempt_answer.dto.attempt_answer_dto import (
    AnswerSubmit,
    AttemptAnswerListResponse,
    AttemptAnswerResponse,
)
from src.app.modules.attempt_answer.service.attempt_answer_exceptions import InvalidAnswerError
from src.app.modules.attempt_answer.service.attempt_answer_service import AttemptAnswerService
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep
from src.app.modules.exam_attempt.model.exam_attempt_model import AttemptStatus, ExamAttempt
from src.app.modules.exam_attempt.service.exam_attempt_exceptions import ExamAttemptNotFoundError
from src.app.modules.exam_attempt.service.exam_attempt_service import ExamAttemptService
from src.app.modules.question.service.question_exceptions import QuestionNotFoundError

router = APIRouter(prefix="/exams/{exam_id}/attempts/{attempt_id}/answers", tags=["attempt-answers"])


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


@router.put("/{question_id}")
async def submit_answer(
    exam_id: int,
    attempt_id: int,
    question_id: int,
    data: AnswerSubmit,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> AttemptAnswerResponse:
    attempt = await _ensure_attempt_owner(exam_id, attempt_id, session, current)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, "Attempt is not in progress")
    try:
        return await AttemptAnswerService(session).submit_answer(attempt_id, question_id, data)
    except QuestionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except InvalidAnswerError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.get("")
async def list_answers(
    exam_id: int, attempt_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> AttemptAnswerListResponse:
    await _ensure_attempt_owner(exam_id, attempt_id, session, current)
    return await AttemptAnswerService(session).list_answers(attempt_id)
