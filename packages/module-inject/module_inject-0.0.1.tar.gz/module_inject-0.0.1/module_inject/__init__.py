import typing
import inspect
import collections.abc
from pathlib import Path
from .module import Module

__all__ = ["get", "Module"]

T = typing.TypeVar("T")


def get_namespace(
    package: bool = False,
    get_path: typing.Callable[[], Path] = lambda: Path(inspect.stack()[2].filename),
) -> collections.abc.Mapping[str, typing.Any]:
    """
    Get namespace for passed module path.

    if package is set to true - gets namespace from directory in which module is stored.
    """
    caller_file = get_path()
    if package:
        caller_file = caller_file.parent

    return Module.from_path(caller_file).namespace.copy()


@typing.overload
def get(name: str, *, package: bool = False, recursive: bool = False) -> typing.Any: ...
@typing.overload
def get(
    name: str, type_: type[T], *, package: bool = False, recursive: bool = False
) -> T: ...
def get(
    name: str,
    type_: typing.Any = None,
    *,
    package: bool = False,
    recursive: bool = False,
) -> typing.Any:
    """
    Get value from caller's module namespace.

    if package is set to True - gets value from module's package namespace.

    if recursive is set to True - walks for all callstack to find the value and returns first entry.
    """
    file_paths = iter(map(lambda x: Path(x.filename), inspect.stack()[1:]))

    while True:
        try:
            namespace = get_namespace(package, lambda: next(file_paths))
        except StopIteration as exc:
            raise KeyError(name) from exc

        if name not in namespace:
            if not recursive:
                raise KeyError(name)
            continue

        value = namespace[name]

        if type_ is not None and not isinstance(value, type_):
            raise TypeError(f'Expected {type_!r} for "{name}", but got {type(value)!r}')

        return value
