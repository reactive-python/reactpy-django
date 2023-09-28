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


class ViewNotRegisteredError(AttributeError):
    ...


class ViewDoesNotExistError(AttributeError):
    ...


class DecoratorParamError(TypeError):
    ...
