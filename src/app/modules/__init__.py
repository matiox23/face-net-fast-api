"""Domain modules. Importing this package registers every ORM model in Base.metadata."""

from src.app.modules.answer_option.model import AnswerOption
from src.app.modules.attempt_answer.model import AttemptAnswer
from src.app.modules.document.model import Document
from src.app.modules.evidence.model import Evidence
from src.app.modules.exam.model import Exam, ExamStatus
from src.app.modules.exam_attempt.model import AttemptStatus, ExamAttempt
from src.app.modules.person.model import Person
from src.app.modules.question.model import Question, QuestionType
from src.app.modules.refresh_token.model import RefreshToken
from src.app.modules.role.model import Role
from src.app.modules.user.model import User, UserStatus
from src.app.modules.user_role.model import UserRole

__all__ = [
    "AnswerOption",
    "AttemptAnswer",
    "AttemptStatus",
    "Document",
    "Evidence",
    "Exam",
    "ExamAttempt",
    "ExamStatus",
    "Person",
    "Question",
    "QuestionType",
    "RefreshToken",
    "Role",
    "User",
    "UserRole",
    "UserStatus",
]
