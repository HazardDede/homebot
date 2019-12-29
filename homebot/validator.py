"""Argument / Attribute validator helper functions."""

from typing import Any, Callable, Iterable, Dict

from typeguard import check_type, typechecked


def is_iterable_but_no_str(candidate: Any) -> bool:
    """
    Checks if the given candidate is an iterable (list, tuple, ...) but not a str instance.

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
    """
    Convenience function for attrs to easily check for a given type by using a validator.
    Remark: typing types like Union[...], List[...] are supported.

    Examples:

        >>> from typing import Optional
        >>> import attr
        >>> @attr.s
        ... class Magic:
        ...     value = attr.ib(validator=attrs_assert_type(Optional[int]))

        >>> Magic(42)  # Valid
        Magic(value=42)
        >>> Magic(None)  # Valid: Optional
        Magic(value=None)
        >>> Magic("str")  # Invalid: no int
        Traceback (most recent call last):
        ...
        TypeError: type of value must be one of (int, NoneType); got str instead

    """
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        check_type(attribute.name, value, expected_type)
    return _validator


def attrs_assert_iterable(expected_type: type) -> Callable[[Any, Any, Any], None]:
    """
    Convenience function for attrs validator to check for an iterable that only contains items of the passed
    `expected_type`.
    Remark: typing types like Union[...], List[...] are supported.

    Examples:

        >>> from typing import Union
        >>> import attr
        >>> @attr.s
        ... class Magic:
        ...     value = attr.ib(validator=attrs_assert_iterable(Union[float, int]))

        >>> Magic([1.0, 2, 3.0])  # Valid
        Magic(value=[1.0, 2, 3.0])
        >>> Magic(42)  # Invalid: no list
        Traceback (most recent call last):
        ...
        TypeError: type of value must be collections.abc.Iterable; got int instead
        >>> Magic([1.0, 2, "str"])
        Traceback (most recent call last):
        ...
        TypeError: type of value[2] must be one of (float, int); got str instead

    """
    def _validator(obj: Any, attribute: Any, value: Any) -> None:
        check_type(attribute.name, value, Iterable)
        for i, item in enumerate(value):
            check_type(f'{attribute.name}[{i}]', item, expected_type)

    return _validator


def _has_type_annotations(fun: Callable[..., Any]) -> bool:
    return hasattr(fun, '__annotations__') and len(fun.__annotations__) > 0


class TypeGuardMeta(type):
    """
    TypeGuard metaclass. Injects decorators to type check calls against __init__
    and __call__ and can_process (if they are defined).

    Examples:

        >>> from typing import Optional, List
        >>> class Magic(metaclass=TypeGuardMeta):
        ...     def __init__(self, i: int, s: Optional[str]):
        ...         self.i = i
        ...         self.s = s
        ...     def can_process(self):
        ...         pass
        ...     def __call__(self, lst: List[int]) -> int:
        ...         return sum(lst)
        ...     def __str__(self):
        ...         return str(self.i) + '__' + str(self.s)

        >>> str(Magic(42, "str"))  # Valid
        '42__str'
        >>> str(Magic(42, None))  # Valid
        '42__None'
        >>> str(Magic("str", None))  # Invalid
        Traceback (most recent call last):
        ...
        TypeError: type of argument "i" must be int; got str instead

        >>> Magic(42, None)([1, 2, 3])
        6
        >>> Magic(42, None)([1, 2, "str"])
        Traceback (most recent call last):
        ...
        TypeError: type of argument "lst"[2] must be int; got str instead

    """

    def __new__(cls, name: str, bases: Any, dct: Dict[Any, Any]) -> type:  # type: ignore
        newly = super().__new__(cls, name, bases, dct)
        if _has_type_annotations(newly.__init__):  # type: ignore
            newly.__init__ = typechecked(always=True)(newly.__init__)  # type: ignore
        if hasattr(newly, '__call__') and _has_type_annotations(newly.__call__):
            newly.__call__ = typechecked(always=True)(newly.__call__)  # type: ignore
        if hasattr(newly, 'can_process') and _has_type_annotations(newly.can_process):  # type: ignore
            newly.can_process = typechecked(always=True)(newly.can_process)  # type: ignore
        return newly
