class ComponentParamError(TypeError):
    ...


class ComponentDoesNotExistError(AttributeError):
    ...


class InvalidHostError(ValueError):
    ...


class ComponentCarrierError(Exception):
    ...


class UserNotFoundError(Exception):
    ...
