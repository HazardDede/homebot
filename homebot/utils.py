"""Utility functions."""

from typing import Any, List, Optional, Callable


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


def make_list(value: Any, null_empty: bool = True) -> Optional[List[Any]]:
    """Makes a list out of the given value. If value is a list, nothing is changed.
    If value is an iterable (but no str), it will be converted to a list. If list is
    either a list nor an iterable it will be converted to a single element list.
    If value is None and null_empty is True an empty list will returned; if null_empty
    is False None will be returned.
    Example:
        >>> make_list(['list'])
        ['list']
        >>> make_list(('t1', 't2'))
        ['t1', 't2']
        >>> make_list('element')
        ['element']
        >>> make_list(None)
        []
        >>> print(make_list(None, null_empty=False))
        None

    """
    if isinstance(value, list):
        return value
    if is_iterable_but_no_str(value):
        return list(value)
    if value is None:
        return [] if null_empty else None
    return [value]


def attrs_assert_type(expected_type: type) -> Callable[[Any, Any, Any], None]:
    """Convenience validator for attrs to check for a given type."""
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        if not isinstance(value, expected_type):
            raise TypeError(f"Attribute '{attribute.name}': Expected {expected_type}, "
                            f"but {type(value)} found.")
    return _validator


def attrs_assert_iterable(expected_type: type) -> Callable[[Any, Any, Any], None]:
    """Convenience validator for attrs to check for an iterable assert that all items
    of that iterable are an instance of the passed expected type."""
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
