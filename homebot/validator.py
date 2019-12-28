"""Argument / Attribute validator helper functions."""

from typing import Any, Callable, Iterable, Dict

from typeguard import check_type, typechecked


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


def _has_type_annotations(fun: Callable[..., Any]) -> bool:
    return hasattr(fun, '__annotations__') and len(fun.__annotations__) > 0


class TypeGuardMeta(type):
    """TypeGuard metaclass. Injects decorators to type check calls against __init__
    and optionally __call__ and can_process."""

    def __new__(cls, name: str, bases: Any, dct: Dict[Any, Any]) -> type:  # type: ignore
        newly = super().__new__(cls, name, bases, dct)
        if _has_type_annotations(newly.__init__):  # type: ignore
            newly.__init__ = typechecked(always=True)(newly.__init__)  # type: ignore
        if hasattr(newly, '__call__') and _has_type_annotations(newly.__call__):
            newly.__call__ = typechecked(always=True)(newly.__call__)  # type: ignore
        if hasattr(newly, 'can_process') and _has_type_annotations(newly.can_process):  # type: ignore
            newly.can_process = typechecked(always=True)(newly.can_process)  # type: ignore
        return newly
