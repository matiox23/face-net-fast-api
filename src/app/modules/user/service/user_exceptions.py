class EmailAlreadyExistsError(Exception):
    """Raised when trying to register a user with an email already in use."""


class UserNotFoundError(Exception):
    """Raised when a user does not exist by id."""
