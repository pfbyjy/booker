import functools
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Tuple, Union

import typer
import inspect

# this is just an "Either", but I prefer the name Outcome as it reads much better
class Outcome(ABC):
    def __init__(
        self, description: str, cause: Exception, context: Dict[str, Any] = {}
    ):
        self.description = description
        self.cause = cause
        self.context = context
        self._resolve_key = None

    def __repr__(self):
        cause_str = "" if self.succeeded() else f"{'Caused by ' + self.cause.__str__()}"
        return f"{self.description} {cause_str}"

    @abstractmethod
    def succeeded(self) -> bool:
        pass

    def failed(self) -> bool:
        return not self.succeeded()

    def set_resolve_key(self, key: str):
        self._resolve_key = key

    def resolve(self) -> Any:
        if self.succeeded():
            return self.context[self._resolve_key]
        return None

    # deprecated
    def get_key(self, kwd: str):
        return self.context[kwd] if kwd in self.context else None

    def get_context(self):
        return self.context

    def with_additional_context(self, kwd: str, val: Any):
        self.context[kwd] = val
        return self


def default_error_handler(outcome: Outcome) -> None:
    if outcome.failed():
        typer.secho(str(outcome), fg=typer.colors.RED)
        raise typer.Exit(1)


class Pipeline:
    def __init__(
        self,
        *,
        error_handler: Callable[[Outcome], Any] = default_error_handler,
        finalizer: Callable[[Any], Any] = None,
        initial_args=None,
    ):
        self.initial_args = {} if initial_args is None else initial_args
        self.error_handler = error_handler
        self.finalizer = finalizer
        self.pending: List[Tuple[Callable[[Any], Outcome], Dict[str, Any]]] = []
        self.initial_args = initial_args
        self.completed: List[Outcome] = [
            SUCCESS(self.initial_args)
        ]  # always begin with the minimal context
        self.executed: bool = False
        self.success: bool = False

    def execute(self) -> Outcome:
        if self.executed:
            return self.completed[-1]
        for i, thunk in enumerate(self.pending):
            prev_context = self.completed[i].get_context()
            action, args = thunk
            # expand the argument to the next call with the context from the previous call
            args = {**prev_context, **args}
            outcome = action(**args)
            # update the context of the outcome so that arguments are propagated
            outcome.context = {**outcome.context, **args}
            self.completed.append(outcome)
            if outcome.failed():
                # if the action fails, run the error handler.
                # if there is no error handler. Give up and return the
                # failing outcome.
                if self.error_handler:
                    self.error_handler(outcome)
                else:
                    self.executed = True
                    self.success = False
                    return outcome
        if self.finalizer:
            if self.finalizer.__code__.co_argcount == 1:
                self.finalizer(self.completed[-1])
            else:
                self.finalizer()
        self.executed = True
        self.success = True
        return self.completed[-1]

    def yield_result(self) -> Any:
        if self.executed:
            return self.completed[-1].resolve()

    def __lshift__(self, action: Callable[[Any], Outcome]) -> "Pipeline":
        self.pending.append((action, {}))
        return self

    def __add__(self, arguments: Dict[str, Any]) -> "Pipeline":
        action, _ = self.pending[-1]
        self.pending[-1] = (action, arguments)
        return self

    def __invert__(self) -> Outcome:
        return self.execute()


class SUCCESS(Outcome):
    def __init__(self, context: Dict[str, Any] = {}):
        super().__init__("success", "", context)

    def succeeded(self) -> bool:
        return True

    def __str__(self):
        return f"Success({list(self.context.keys())}"

    def __repr__(self):
        return f"Success({list(self.context)}"


class ERROR(Outcome, ABC):
    def __init__(self, description: str, cause: Exception):
        super().__init__(description, cause)

    def succeeded(self) -> bool:
        return False


class GenericError(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("Something unexpected went wrong", cause)


class Argument:
    def __init__(self, key, optional=False, use_default=False, default=None):
        self.key = key
        self.optional = optional
        self.use_default = use_default
        self.default = default

    def get(self, args: Dict[str, Any]) -> Any:
        if self.key in args:
            return args[self.key]
        if self.use_default:
            return self.default
        return None


def outcome(
    *, requires: Tuple[Union[Argument, str], ...] = None, returns=None, registers=None
):
    requires = () if requires is None else requires
    returns = "" if returns is None else returns
    registers = {} if registers is None else registers

    def outcome_shell(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # if the function is called with arguments, then treat it as a regular function call.
            calling_file = inspect.currentframe().f_back.f_code.co_name
            # this has a very weird edge case with functions that have one default argument.
            if len(args) > 0:
                return func(*args)

            new_args = {}
            for arg in requires:
                val = arg.get(kwargs)
                if val is not None:
                    new_args[arg.key] = val
            try:
                temp = func(**new_args)
            except Exception as e:
                if e in registers.keys():
                    handler = registers[type(e)]
                else:
                    handler = GenericError
                return handler(e)
            if returns == "":
                return SUCCESS()
            o = SUCCESS({returns: temp})
            o.set_resolve_key(returns)
            return o

        return wrapper

    requires = [Argument(key) if type(key) == str else key for key in requires]
    return outcome_shell
