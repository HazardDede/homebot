"""Utility functions."""

from typing import Any, cast, Iterable


def is_iterable_but_no_str(candidate: Any) -> bool:
    """
    Checks if the given candidate is an iterable but not a str instance
    Example:
        >>> is_iterable_but_no_str(['a'])
        True
        >>> is_iterable_but_no_str('a')
        False
        >>> is_iterable_but_no_str(None)
        False
    """
    return hasattr(candidate, '__iter__') and not isinstance(candidate, (str, bytes))


def make_list(value: Any) -> Iterable[Any]:
    return cast(Iterable[Any], value) if is_iterable_but_no_str(value) else [value]


def attrs_assert_type(expected_type: type):
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        if not isinstance(value, expected_type):
            raise TypeError(f"Attribute '{attribute.name}': Expected {expected_type}, "
                            f"but {type(value)} found.")
    return _validator


def attrs_assert_iterable(expected_type: type):
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        if not is_iterable_but_no_str(value):
            raise TypeError(f"Attribute '{attribute.name}': Expected an iterable, "
                            f"but {type(value)} found.")
        for i, item in enumerate(value):
            if not isinstance(item, expected_type):
                raise TypeError(f"Attribute '{attribute.name}': "
                                f"Expected {expected_type} for list item @ index {i}, "
                                f"but is {type(item)}")
    return _validator
