from enum import Enum
from typing import Callable, Any


class Error(Enum):
    SUCCESS = 0
    CONFIG_DIRECTORY_ERROR = 1
    CONFIG_FILE_ERROR = 2
    DB_READ_ERROR = 3
    DB_WRITE_ERROR = 4
    JSON_ERROR = 5
    ID_ERROR = 6


class Outcome:
    def __init__(self, err: Error, cause: Exception):
        self.err = err
        self.cause = cause

    def _effect(self):
        return {
            Error.SUCCESS: "success",
            Error.CONFIG_DIRECTORY_ERROR: "something went wrong with the config directory",
            Error.CONFIG_FILE_ERROR: "something went wrong with the config file",
            Error.DB_READ_ERROR: "something went wrong reading from database",
            Error.DB_WRITE_ERROR: "something went wrong writing to the database",
            Error.ID_ERROR: "something went wrong with the id supplied",
            Error.JSON_ERROR: "something is wrong with the supplied JSON file."
        }[self.err]

    def __repr__(self):
        return f'{self.err}: {self._effect()}, caused by {self.cause.__repr__()}'

    def succeeded(self) -> bool:
        return self.err == Error.SUCCESS

    def failed(self)-> bool:
        return not self.succeeded()

    def is_error(self, error_type: Error) -> bool :
        return self.err == error_type


SUCCESS = Outcome(Error.SUCCESS, "")
CONFIG_DIRECTORY_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.CONFIG_DIRECTORY_ERROR, cause)
CONFIG_FILE_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.CONFIG_FILE_ERROR, cause)
DB_READ_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.DB_READ_ERROR, cause)
DB_WRITE_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.DB_WRITE_ERROR, cause)
JSON_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.JSON_ERROR, cause)
ID_ERROR: Callable[[Exception], Outcome] = lambda cause: Outcome(Error.ID_ERROR, cause)
