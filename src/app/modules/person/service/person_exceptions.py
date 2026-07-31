class PersonNotFoundError(Exception):
    """Raised when a person does not exist by id."""


class PersonDocumentAlreadyExistsError(Exception):
    """Raised when a person with the same document type and number already exists."""
