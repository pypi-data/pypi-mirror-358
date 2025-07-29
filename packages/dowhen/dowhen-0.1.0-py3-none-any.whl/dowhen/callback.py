# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/dowhen/blob/master/NOTICE


from __future__ import annotations

import ctypes
import inspect
import sys
import warnings
from collections.abc import Callable
from types import CodeType, FrameType, FunctionType, MethodType, ModuleType
from typing import TYPE_CHECKING, Any

from .util import call_in_frame, get_line_numbers

if TYPE_CHECKING:  # pragma: no cover
    from .handler import EventHandler


DISABLE = sys.monitoring.DISABLE


class Callback:
    def __init__(self, func: str | Callable, **kwargs):
        if isinstance(func, str):
            pass
        elif inspect.isfunction(func):
            self.func_args = inspect.getfullargspec(func).args
        elif inspect.ismethod(func):
            self.func_args = inspect.getfullargspec(func).args
        else:
            raise TypeError(f"Unsupported callback type: {type(func)}. ")
        self.func = func
        self.kwargs = kwargs

    def __call__(self, frame, **kwargs) -> Any:
        ret = None
        if isinstance(self.func, str):
            if self.func == "goto":  # pragma: no cover
                self._call_goto(frame)
            else:
                self._call_code(frame)
        elif inspect.isfunction(self.func) or inspect.ismethod(self.func):
            ret = self._call_function(frame, **kwargs)
        else:  # pragma: no cover
            assert False, "Unknown callback type"

        if sys.version_info < (3, 13):
            LocalsToFast = ctypes.pythonapi.PyFrame_LocalsToFast
            LocalsToFast.argtypes = [ctypes.py_object, ctypes.c_int]
            LocalsToFast(frame, 0)

        if ret is DISABLE:
            return DISABLE

    def _call_code(self, frame: FrameType) -> None:
        assert isinstance(self.func, str)
        exec(self.func, frame.f_globals, frame.f_locals)

    def _call_function(self, frame: FrameType, **kwargs) -> Any:
        assert isinstance(self.func, (FunctionType, MethodType))
        writeback = call_in_frame(self.func, frame, **kwargs)

        f_locals = frame.f_locals
        if isinstance(writeback, dict):
            for arg, val in writeback.items():
                if arg not in f_locals:
                    raise TypeError(f"Argument '{arg}' not found in frame locals.")
                f_locals[arg] = val
        elif writeback is DISABLE:
            return DISABLE
        elif writeback is not None:
            raise TypeError(
                "Callback function must return a dictionary for writeback, or None, "
                f"got {type(writeback)} instead."
            )

    def _call_goto(self, frame: FrameType) -> None:  # pragma: no cover
        # Changing frame.f_lineno is only allowed in trace functions so it's
        # impossible to get coverage for this function
        target = self.kwargs["target"]
        line_numbers = get_line_numbers(frame.f_code, target)
        if line_numbers is None:
            raise ValueError(f"Could not determine line number for target: {target}")
        elif len(line_numbers) > 1:
            raise ValueError(
                f"Multiple line numbers found for target '{target}': {line_numbers}"
            )
        line_number = line_numbers[0]
        with warnings.catch_warnings():
            # This gives a RuntimeWarning in Python 3.12
            warnings.simplefilter("ignore", RuntimeWarning)
            # mypy thinks f_lineno is read-only
            frame.f_lineno = line_number  # type: ignore

    @classmethod
    def do(cls, func: str | Callable) -> Callback:
        return cls(func)

    @classmethod
    def goto(cls, target: str | int) -> Callback:
        return cls("goto", target=target)

    @classmethod
    def bp(cls) -> Callback:
        def do_breakpoint(_frame: FrameType) -> None:  # pragma: no cover
            import pdb

            p = pdb.Pdb()
            p.set_trace(_frame)
            if hasattr(p, "set_enterframe"):
                # set_enterframe is backported to 3.12 so the early versions
                # of Python 3.12 will not have this method
                with p.set_enterframe(_frame):
                    p.user_line(_frame)
            else:
                p.user_line(_frame)

        return cls(do_breakpoint)

    def when(
        self,
        entity: CodeType | FunctionType | MethodType | ModuleType | type | None,
        *identifiers: str | int | tuple,
        condition: str | Callable[..., bool | Any] | None = None,
        source_hash: str | None = None,
    ) -> "EventHandler":
        from .trigger import when

        trigger = when(
            entity, *identifiers, condition=condition, source_hash=source_hash
        )

        from .handler import EventHandler

        handler = EventHandler(trigger, self)
        handler.submit()

        return handler


bp = Callback.bp
do = Callback.do
goto = Callback.goto
