from typing import get_origin, get_args


def is_matrix(type_hint: type) -> bool:
    """
    Checks if the given type hint represents a matrix (list of lists).

    Args:
        type_hint (Type): The type hint to check.

    Returns:
        bool: True if the type hint is a matrix, False otherwise.
    """
    if get_origin(type_hint) is list:
        inner_type = get_args(type_hint)
        if inner_type and get_origin(inner_type[0]) is list:
            return True
    return False
