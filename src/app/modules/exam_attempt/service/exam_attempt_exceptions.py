class ExamAttemptNotFoundError(Exception):
    """Raised when an attempt does not exist."""


class ExamNotPublishedError(Exception):
    """Raised when trying to start an attempt on an exam that is not PUBLISHED."""


class AttemptAlreadyExistsError(Exception):
    """Raised when a student already has an attempt for this exam."""


class AttemptNotInProgressError(Exception):
    """Raised when trying to answer or submit an attempt that is not IN_PROGRESS."""
