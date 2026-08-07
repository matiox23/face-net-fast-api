from fastapi import FastAPI

from src.app.modules.answer_option.controller.answer_option_controller import (
    router as answer_option_router,
)
from src.app.modules.auth.controller.auth_controller import router as auth_router
from src.app.modules.exam.controller.exam_controller import router as exam_router
from src.app.modules.question.controller.question_controller import router as question_router
from src.app.modules.user.controller.user_controller import router as user_router
from src.app.modules.user_role.controller.user_role_controller import router as user_role_router

app = FastAPI(title="Face Net API")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(user_role_router)
app.include_router(exam_router)
app.include_router(question_router)
app.include_router(answer_option_router)
