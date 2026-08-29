"""Errors about who is asking and what exists. Domain rules live in app.domain.errors."""


class ServiceError(Exception):
    pass


class NotFound(ServiceError):
    pass


class Forbidden(ServiceError):
    pass
