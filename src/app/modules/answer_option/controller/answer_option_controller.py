from fastapi import APIRouter, HTTPException, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.answer_option.dto.answer_option_dto import (
    AnswerOptionCreate,
    AnswerOptionListResponse,
    AnswerOptionResponse,
    AnswerOptionUpdate,
)
from src.app.modules.answer_option.service.answer_option_exceptions import (
    AnswerOptionNotFoundError,
)
from src.app.modules.answer_option.service.answer_option_service import AnswerOptionService
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep
from src.app.modules.exam.service.exam_exceptions import ExamNotFoundError
from src.app.modules.exam.service.exam_service import ExamService
from src.app.modules.question.service.question_exceptions import QuestionNotFoundError
from src.app.modules.question.service.question_service import QuestionService

router = APIRouter(
    prefix="/exams/{exam_id}/questions/{question_id}/options", tags=["answer-options"]
)


async def _ensure_question_owner_or_admin(
    exam_id: int, question_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> None:
    try:
        exam = await ExamService(session).get_exam_entity(exam_id)
    except ExamNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if exam.teacher_id != current.user.id and "ADMIN" not in current.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")

    try:
        question = await QuestionService(session).get_question_entity(question_id)
    except QuestionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if question.exam_id != exam_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question does not belong to this exam")


async def _ensure_option_in_question(
    question_id: int, option_id: int, session: AsyncSessionDep
) -> None:
    try:
        option = await AnswerOptionService(session).get_option_entity(option_id)
    except AnswerOptionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if option.question_id != question_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Option does not belong to this question")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_option(
    exam_id: int,
    question_id: int,
    data: AnswerOptionCreate,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> AnswerOptionResponse:
    await _ensure_question_owner_or_admin(exam_id, question_id, session, current)
    return await AnswerOptionService(session).create_option(question_id, data)


@router.get("")
async def list_options(
    exam_id: int, question_id: int, session: AsyncSessionDep, current: CurrentUserDep
) -> AnswerOptionListResponse:
    await _ensure_question_owner_or_admin(exam_id, question_id, session, current)
    return await AnswerOptionService(session).list_options(question_id)


@router.get("/{option_id}")
async def get_option(
    exam_id: int,
    question_id: int,
    option_id: int,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> AnswerOptionResponse:
    await _ensure_question_owner_or_admin(exam_id, question_id, session, current)
    await _ensure_option_in_question(question_id, option_id, session)
    return await AnswerOptionService(session).get_option(option_id)


@router.patch("/{option_id}")
async def update_option(
    exam_id: int,
    question_id: int,
    option_id: int,
    data: AnswerOptionUpdate,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> AnswerOptionResponse:
    await _ensure_question_owner_or_admin(exam_id, question_id, session, current)
    await _ensure_option_in_question(question_id, option_id, session)
    return await AnswerOptionService(session).update_option(option_id, data)


@router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_option(
    exam_id: int,
    question_id: int,
    option_id: int,
    session: AsyncSessionDep,
    current: CurrentUserDep,
) -> None:
    await _ensure_question_owner_or_admin(exam_id, question_id, session, current)
    await _ensure_option_in_question(question_id, option_id, session)
    await AnswerOptionService(session).delete_option(option_id)
