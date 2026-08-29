"""Domain errors. Each one names the rule it protects."""


class DomainError(Exception):
    """Base for rules the domain refuses to break."""


class NotAMember(DomainError):
    """Invariant 2: the member is not in this Circle."""


class MeetingNotInCircle(DomainError):
    """Invariant 2: the meeting belongs to another Circle."""


class DuplicateAction(DomainError):
    """Invariant 1: this member already has an action for this meeting."""


class InvalidStatusTransition(DomainError):
    """Invariant 3: status never returns to committed."""
