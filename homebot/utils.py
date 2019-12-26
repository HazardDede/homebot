"""Utility functions."""
import inspect
import logging
from typing import Any, List, Optional, Callable, cast, Iterable, Set


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


class classproperty(property):  # pylint: disable=invalid-name
    """
    Decorator classproperty:
    Make class methods look like read-only class properties.
    Writing to that classproperty will not do what you expect ;-)
    Examples:
        >>> class Foo(object):
        ...     _instance = 5
        ...     @classproperty
        ...     def my_prop(cls):
        ...         return cls._instance
        >>> Foo.my_prop
        5
        >>> Foo._instance
        5
        >>> Foo._instance = 15
        >>> Foo.my_prop
        15
        >>> Foo.my_prop = 10
        >>> Foo._instance
        15
    """
    def __get__(self, cls, owner):  # type: ignore
        return classmethod(self.fget).__get__(None, owner)()


class AutoStrMixin:
    """
    Magically adds __str__ and __repr__ methods containing non-ignored fields.

    Example:

        >>> class Magic(AutoStrMixin):
        ...     __ignore_fields__ = ['c']
        ...     def __init__(self):
        ...         self.a = 42
        ...         self.b = 'abc'
        ...         self.c = 42.42

        >>> class MoreMagic(Magic):
        ...     __ignore_fields__ = ['e']
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.d = 'd'
        ...         self.e = 'e'

        >>> dut = Magic()
        >>> str(dut)
        "Magic(a=42, b='abc')"
        >>> repr(dut)
        "Magic(a=42, b='abc')"
        >>> mm = MoreMagic()
        >>> str(mm)
        "MoreMagic(a=42, b='abc', d='d')"
    """

    @classmethod
    def __ignore(cls) -> Set[str]:
        clz = cls
        field_name = '__ignore_fields__'
        res: Set[str] = set()

        for clazz in inspect.getmro(clz):
            values_ = getattr(clazz, field_name, None)
            if values_ is not None:
                res = res.union(set(cast(Iterable[str], make_list(values_))))
        return res

    def __str__(self) -> str:
        items = [
            "{name}={value}".format(
                name=name,
                value=vars(self)[name].__repr__()
            ) for name in sorted(vars(self))
            if name not in self.__ignore()
        ]
        return "{clazz}({items})".format(
            clazz=str(type(self).__name__),
            items=', '.join(items)
        )

    def __repr__(self) -> str:
        return str(self)


class LogMixin:
    """
    Adds a logger property to the class to provide easy access to a configured logging instance to
    use.
    Example:
        >>> class NeedsLogger(LogMixin):
        ...     def do(self, message):
        ...         self.logger.info(message)
        >>> dut = NeedsLogger()
        >>> dut.do('mymessage')
    """
    @classproperty
    def logger(cls: Any) -> logging.Logger:  # pylint: disable=no-self-argument
        """
        Configures and returns a logger instance for further use.
        Returns:
            (logging.Logger)
        """
        component = "{}.{}".format(cls.__module__, cls.__name__)  # pylint: disable=no-member
        return logging.getLogger(component)
