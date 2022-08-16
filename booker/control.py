from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Tuple
import typer


# this is just an "Either", but I prefer the name Outcome as it reads much better
class Outcome(ABC):
    def __init__(self, description: str, cause: Exception, context: Dict[str, Any] = {}):
        self.description = description
        self.cause = cause
        self.context = context

    def __repr__(self):
        cause_str = '' if self.succeeded() else f"{' Caused by ' + self.cause.__str__()}"
        return f"{self.description} {cause_str}"

    @abstractmethod
    def succeeded(self) -> bool:
        pass

    def failed(self) -> bool:
        return not self.succeeded()

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


class OutcomeChain:
    def __init__(
            self,
            error_handler: Callable[[Outcome], Any] = default_error_handler,
            finalizer: Callable[[Any], Any] = None,
    ):
        self.error_handler = error_handler
        self.finalizer = finalizer
        self.pending: List[Tuple[Callable[[Any], Outcome], Dict[str, Any]]] = []
        self.completed: List[Outcome] = [SUCCESS()]  # always begin with the minimal context
        self.executed: bool = False
        self.success: bool = False

    def execute(self):
        for i, thunk in enumerate(self.pending):
            prev_context = self.completed[i].get_context()
            action, args = thunk
            # expand the argument to the next call with the context from the previous call
            args = {**args, **prev_context}
            outcome = action(**args)
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
            self.finalizer()
        self.executed = True
        self.success = True
        return self.completed[-1]

    def yield_result(self, kwd: str) -> Any:
        if self.executed:
            return self.completed[-1].get_key(kwd)

    def with_initial_context(self, kwd: str, val: Any):
        self.completed[0].with_additional_context(kwd, val)
        return self

    # all arguments must be keyword arguments
    def sequence(self, action: Callable[[Any], Outcome], arguments: Dict[str, Any] = {}):
        self.pending.append((action, arguments))
        return self


class SUCCESS(Outcome):
    def __init__(self, context: Dict[str, Any] = {}):
        super().__init__("success", "", context)

    def succeeded(self) -> bool:
        return True


class ERROR(Outcome, ABC):
    def __init__(self, description: str, cause: Exception):
        super().__init__(description, cause)

    def succeeded(self) -> bool:
        return False
