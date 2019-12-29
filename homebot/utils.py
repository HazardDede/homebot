"""Utility functions."""
import inspect
import logging
from typing import Any, List, Optional, cast, Iterable, Set

from homebot.validator import is_iterable_but_no_str


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


def interpolate(format_: str, **context: Any) -> str:
    """
    Dynamically interpolates a format by using a given context.

    Example:

        >>> interpolate('{payload}', payload=12)
        '12'
        >>> interpolate('{payload.upper()}', payload="a")
        'A'
        >>> interpolate('{(a - b):0.2f}', a=10, b=4.999)
        '5.00'
    """
    return cast(str, eval(f'f{format_!r}', None, context))  # pylint: disable=eval-used


def interpolate_complex(cplx: Any, **context: Any) -> Any:
    """
    f-String interpolates a complex structure (like a dict or list).

    Examples:

        >>> dut = interpolate_complex
        >>> dut("{number}", number=42)  # str
        '42'
        >>> dut(["{one}", "{two}"], one=1, two=2)  # list
        ['1', '2']
        >>> dut(("{one}", "{two}"), one=1, two=2)  # tuple
        ['1', '2']
        >>> dut({'one': '{one}', '{two}': 'two'}, one=1, two=2)  # dict
        {'one': '1', '2': 'two'}
        >>> dut({'one': '{one}', '{two}': ["{one}", "{two}"]}, one=1, two=2)  # complex
        {'one': '1', '2': ['1', '2']}
        >>> dut(42, one=1, two=2)  # none of the above -> as is
        42
    """
    # pylint: disable=invalid-name
    def i(c: Any) -> Any:
        if isinstance(c, dict):
            return {i(k): i(v) for k, v in c.items()}
        if is_iterable_but_no_str(c):
            return [i(item) for item in c]
        if isinstance(c, str):
            return interpolate(c, **context)
        return c

    # pylint: enable=invalid-name

    return i(cplx)


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
