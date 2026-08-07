class QuestionNotFoundError(Exception):
    """Raised when a question does not exist or is soft-deleted."""


class QuestionOrderConflictError(Exception):
    """Raised when `order` is already used by another question in the same exam."""
