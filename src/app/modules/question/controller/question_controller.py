from fastapi import APIRouter, HTTPException, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep
from src.app.modules.exam.model.exam_model import Exam
from src.app.modules.exam.service.exam_exceptions import ExamNotFoundError
from src.app.modules.exam.service.exam_service import ExamService
from src.app.modules.question.dto.question_dto import (
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdate,
)
from src.app.modules.question.model.question_model import Question
from src.app.modules.question.service.question_exceptions import QuestionNotFoundError
from src.app.modules.question.service.question_service import QuestionService

router = APIRouter(prefix="/exams/{exam_id}/questions", tags=["questions"])


async def _ensure_exam_owner_or_admin(
    exam_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> Exam:
    try:
        exam = await ExamService(session).get_exam_entity(exam_id)
    except ExamNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if exam.teacher_id != current.user.id and "ADMIN" not in current.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    return exam


async def _ensure_question_in_exam(
    exam_id: int, question_id: int, session: AsyncSessionDep
) -> Question:
    try:
        question = await QuestionService(session).get_question_entity(question_id)
    except QuestionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if question.exam_id != exam_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question does not belong to this exam")
    return question


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_question(
    exam_id: int, data: QuestionCreate, session: AsyncSessionDep, current: CurrentUserDep
) -> QuestionResponse:
    await _ensure_exam_owner_or_admin(exam_id, session, current)
    return await QuestionService(session).create_question(exam_id, data)


@router.get("")
async def list_questions(
    exam_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> QuestionListResponse:
    await _ensure_exam_owner_or_admin(exam_id, session, current)
    return await QuestionService(session).list_questions(exam_id)


@router.get("/{question_id}")
async def get_question(
    exam_id: int, question_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> QuestionResponse:
    await _ensure_exam_owner_or_admin(exam_id, session, current)
    await _ensure_question_in_exam(exam_id, question_id, session)
    return await QuestionService(session).get_question(question_id)


@router.patch("/{question_id}")
async def update_question(
    exam_id: int,
    question_id: int,
    data: QuestionUpdate,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> QuestionResponse:
    await _ensure_exam_owner_or_admin(exam_id, session, current)
    await _ensure_question_in_exam(exam_id, question_id, session)
    return await QuestionService(session).update_question(question_id, data)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    exam_id: int, question_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> None:
    await _ensure_exam_owner_or_admin(exam_id, session, current)
    await _ensure_question_in_exam(exam_id, question_id, session)
    await QuestionService(session).delete_question(question_id)
