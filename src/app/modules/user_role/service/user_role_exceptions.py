class RoleAlreadyAssignedError(Exception):
    """Raised when trying to assign a role a user already has."""


class RoleNotAssignedError(Exception):
    """Raised when trying to revoke a role a user does not have."""
