"""Argument / Attribute validator helper functions."""

from typing import Any, Callable, Iterable

from typeguard import check_type


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


def attrs_assert_type(expected_type: type) -> Callable[[Any, Any, Any], None]:
    """Convenience validator for attrs to check for a given type."""
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        check_type(attribute.name, value, expected_type)
    return _validator


def attrs_assert_iterable(expected_type: type) -> Callable[[Any, Any, Any], None]:
    """Convenience validator for attrs to check for an iterable assert that all items
    of that iterable are an instance of the passed expected type."""
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        check_type(attribute.name, value, Iterable[expected_type])  # type: ignore

    return _validator
