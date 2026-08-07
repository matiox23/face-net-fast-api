from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep, require_roles
from src.app.modules.exam.dto.exam_dto import (
    ExamCreate,
    ExamListResponse,
    ExamResponse,
    ExamStatusUpdate,
    ExamUpdate,
)
from src.app.modules.exam.service.exam_exceptions import ExamNotFoundError
from src.app.modules.exam.service.exam_service import ExamService

router = APIRouter(prefix="/exams", tags=["exams"])


async def _ensure_owner_or_admin(exam_id: int, session: AsyncSessionDep, current: CurrentUserDep):
    try:
        exam = await ExamService(session).get_exam_entity(exam_id)
    except ExamNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if exam.teacher_id != current.user.id and "ADMIN" not in current.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    return exam


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("TEACHER", "ADMIN"))])
async def create_exam(data: ExamCreate, session: AsyncSessionDep, current: CurrentUserDep) -> ExamResponse:
    return await ExamService(session).create_exam(current.user.id, data)


@router.get("")
async def list_exams(
    session: AsyncSessionDep,
    current: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ExamListResponse:
    teacher_id = None if "ADMIN" in current.roles else current.user.id
    return await ExamService(session).list_exams(page, page_size, teacher_id)


@router.get("/{exam_id}")
async def get_exam(exam_id: int, session: AsyncSessionDep, current: CurrentUserDep) -> ExamResponse:
    await _ensure_owner_or_admin(exam_id, session, current)
    return await ExamService(session).get_exam(exam_id)


@router.patch("/{exam_id}")
async def update_exam(
    exam_id: int, data: ExamUpdate, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamResponse:
    await _ensure_owner_or_admin(exam_id, session, current)
    return await ExamService(session).update_exam(exam_id, data)


@router.patch("/{exam_id}/status")
async def update_exam_status(
    exam_id: int, data: ExamStatusUpdate, session: AsyncSessionDep, current: CurrentUserDep
) -> ExamResponse:
    await _ensure_owner_or_admin(exam_id, session, current)
    return await ExamService(session).update_status(exam_id, data.status)


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(exam_id: int, session: AsyncSessionDep, current: CurrentUserDep) -> None:
    await _ensure_owner_or_admin(exam_id, session, current)
    await ExamService(session).delete_exam(exam_id)
