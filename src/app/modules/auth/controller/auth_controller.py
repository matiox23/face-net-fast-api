from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep
from src.app.modules.auth.dto.auth_dto import LogoutRequest, RefreshRequest, TokenResponse
from src.app.modules.auth.service.auth_exceptions import InvalidCredentialsError
from src.app.modules.auth.service.auth_service import AuthService
from src.app.modules.refresh_token.service.refresh_token_exceptions import InvalidRefreshTokenError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSessionDep
) -> TokenResponse:
    try:
        return await AuthService(session).login(form_data.username, form_data.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc


@router.post("/refresh")
async def refresh(data: RefreshRequest, session: AsyncSessionDep) -> TokenResponse:
    try:
        return await AuthService(session).refresh(data)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: LogoutRequest, session: AsyncSessionDep, current: CurrentUserDep) -> None:
    await AuthService(session).logout(data)
