class AnswerOptionNotFoundError(Exception):
    """Raised when an answer option does not exist or is soft-deleted."""


class AnswerOptionOrderConflictError(Exception):
    """Raised when `order` is already used by another option in the same question."""
