class ComponentParamError(TypeError):
    ...


class ComponentDoesNotExistError(AttributeError):
    ...


class InvalidHostError(ValueError):
    ...


class ComponentCarrierError(ValueError):
    ...


class ViewNotRegisteredError(AttributeError):
    ...


class ViewDoesNotExistError(AttributeError):
    ...
