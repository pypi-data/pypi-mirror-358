# import pysnooper

from functools import partial
from typing import get_type_hints, get_origin, Annotated, get_args, Callable, Type, Any

from kaya_module_sdk.src.utils.metadata.variadic import Variadic
from kaya_module_sdk.src.utils.check import is_matrix
from kaya_module_sdk.src.datatypes.classifier import KClassifier


# @pysnooper.snoop()
def kaya_io() -> Callable:
    def wrapper(cls: type) -> type:
        annotations = get_type_hints(cls, include_extras=True)
        # NOTE: Build the __init__ signature and method body
        parameter_lines, body_lines = build_class_structure(cls, annotations)
        # NOTE: Generate and attach the dynamic `__init__` method
        attach_init_method(cls, parameter_lines, body_lines)
        return cls

    return wrapper


# @pysnooper.snoop()
def build_class_structure(cls: type, annotations: dict[str, Any]) -> tuple[list[str], list[str]]:
    """
    Build the list of parameters and the initialization body for the class.
    """
    parameter_lines = []
    body_lines = []
    for field_name, field_type in annotations.items():
        # NOTE: Process fields with Annotated types only
        if get_origin(field_type) is not Annotated:
            continue
        if field_name in ["_results"]:  # "_errors",
            continue
        base_type = get_args(field_type)[0]
        metadata = get_args(field_type)[1:]
        variadic = next((meta for meta in metadata if isinstance(meta, Variadic)), None)
        if variadic or is_matrix(base_type):
            # NOTE: Supports 2D matrix only for variadic input fields
            base_type = get_args(get_args(get_args(field_type)[0])[0])[0]
        add_getter_and_setter(cls, field_name, base_type)
        # optional_type = Union[base_type, None]  # Optional[type]
        parameter_lines.append(build_parameter(field_name, base_type))
        body_lines.append(build_body_line(field_name))
    return parameter_lines, body_lines


# @pysnooper.snoop()
def add_getter_and_setter(cls: Type[Any], field_name: str, base_type: Type) -> None:
    """
    Dynamically create and attach getter and setter methods for a given field.
    """
    getter_func = partial(create_getter, field_name=field_name)
    setter_func = partial(create_setter, field_name=field_name)
    setattr(cls, field_name.lstrip("_"), getter_func())
    setattr(cls, f'set_{field_name.lstrip("_")}', setter_func())


# @pysnooper.snoop()
def build_parameter(field_name: str, base_type: Type[Any]) -> str:
    """
    Build a string representation of a parameter for the dynamic __init__ method.
    """
    return f"{field_name.strip('_')}: {base_type.__name__} | None = None"


# @pysnooper.snoop()
def build_body_line(field_name: str) -> str:
    """
    Build a line of code for the __init__ method body to set instance attributes.
    """
    body_line = f"if {field_name.strip('_')} is not None: self.set_{field_name.strip('_')}({field_name.strip('_')})"
    return body_line


# @pysnooper.snoop()
def attach_init_method(cls: Type, parameter_lines: list[str], body_lines: list[str]) -> None:
    """
    Dynamically create and attach the __init__ method to the class.
    """
    init_code = f"""def __init__(self, {', '.join(parameter_lines)}):\n\
        super(type(self), self).__init__()\n\
        {'\n        '.join(body_lines)}"""
    namespace: dict = {}
    constructor: str = "__init__"
    exec(init_code, globals(), namespace)
    setattr(cls, constructor, namespace[constructor])


# NOTE: Placeholder functions for getter and setter creation
# @pysnooper.snoop()
def create_getter(field_name: str) -> Callable:
    @property  # type: ignore
    def getter(self: Type) -> Any:
        return getattr(self, field_name, None)

    return getter


# @pysnooper.snoop()
def create_setter(field_name: str) -> Callable:
    def setter(self: Type, value: Any) -> None:
        setattr(self, field_name, value)

    return setter


# CODE DUMP
