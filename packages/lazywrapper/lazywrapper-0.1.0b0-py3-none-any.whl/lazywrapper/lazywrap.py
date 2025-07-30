from collections.abc import Callable
from typing import Any, Optional
from warnings import warn


class LazyWrap:
    def __init__(
        self,
        loader: Callable[[Any, ...], Any],
        *args,
        lazy_args: tuple[Any, ...] = None,
        lazy_kwargs: dict[str, Any] = None,
        **kwargs,
    ):
        """
        A lazy object class: loader object will only be called when LazyWrap object
        is called.

        :param loader: any callable object, i.e. method, class, etc.
        :param args: args to pass into loader
        :param lazy_args: LazyWrap objects to call when this object calls, and pass to loader as args
        :param lazy_kwargs: LazyWrap objects to call when this object calls, and pass to loader as kwargs
        :param kwargs: kwargs to pass into loader
        """
        self._loader: Callable[[Any, ...], Any] = loader
        self._args: tuple[Any, ...] = args
        self._kwargs: dict[str, Any] = kwargs
        self._lazy_args: tuple[Any, ...] = lazy_args
        self._lazy_kwargs: dict[str, Any] = lazy_kwargs
        self._value: Optional[Any] = None

    def __call__(self, *args, **kwargs) -> Any:
        """

        :param args: args to pass into loader (overrides args from initial instance)
        :param kwargs: kwargs to pass into loader (overrides kwargs from initial instance)
        :return: return value of loader when called
        """
        if args:
            if self._args:
                warn("overriding args from __init__", UserWarning)
            self._args = args
        if kwargs:
            if self._kwargs:
                warn("overriding kwargs from __init__", UserWarning)
            self._kwargs = kwargs
        if self._value is not None:
            return self._value
        self._load_lazy()
        self._value = self._loader(*self._args, **self._kwargs)
        return self._value

    def _load_lazy(self) -> None:
        """
        Calls self._load_lazy_args() and self._load_lazy_kwargs() and checks for TypeError

        :return: None
        """
        try:
            self._load_lazy_args()
            self._load_lazy_kwargs()
        except TypeError as type_err:
            raise TypeError(f"invalid lazy_arg - {type_err}")

    def _load_lazy_args(self) -> None:
        """
        Calls all the args in self._lazy_args and appends to self._args

        :return: None
        """
        if self._lazy_args is None:
            return
        if not isinstance(self._lazy_args, tuple):
            raise TypeError("Invalid lazy_args: must be in tuple")
        arg_ls = list(self._args)
        for arg in self._lazy_args:
            arg_ls.append(arg())
        self._args = tuple(arg_ls)

    def _load_lazy_kwargs(self) -> None:
        """
        Calls all the kwargs in self._lazy_kwargs and appends to self._kwargs

        :return: None
        """
        if self._lazy_kwargs is None:
            return
        if not isinstance(self._lazy_kwargs, dict):
            raise TypeError("Invalid lazy_kwargs: must be in dict")
        for key, var in self._lazy_kwargs.items():
            self._kwargs[key] = var()
