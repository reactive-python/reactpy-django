class ComponentParamError(TypeError):
    ...


class ComponentDoesNotExistError(AttributeError):
    ...


class InvalidHostError(ValueError):
    ...


class ComponentCarrierError(ValueError):
    ...


class ComponentNotRegisteredError(ComponentDoesNotExistError):
    ...
