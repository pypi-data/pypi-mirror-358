from typing import Callable, Generic, Optional, TypeVar, Union, final, cast

F = TypeVar("F")
T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class Result(Generic[T, E]):
    """
    Result is a type that represents either success (Ok) or failure (Err).
    """

    def __init__(self) -> None:
        # This class should not be instantiated directly.
        # Use Ok(value) or Err(error) instead.
        raise TypeError("Cannot instantiate Result directly.")

    def ok(self) -> Optional[T]:
        raise NotImplementedError

    def err(self) -> Optional[E]:
        raise NotImplementedError

    def map(self, op: Callable[[T], U]) -> "Result[U, E]":
        raise NotImplementedError

    def map_err(self, op: Callable[[E], F]) -> "Result[T, F]":
        raise NotImplementedError

    def and_then(self, op: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        raise NotImplementedError

    def or_else(self, op: Callable[[E], "Result[T, F]"]) -> "Result[T, F]":
        raise NotImplementedError

    def unwrap(self) -> T:
        raise NotImplementedError

    def unwrap_err(self) -> E:
        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        raise NotImplementedError

    def contains(self, value: T) -> bool:
        raise NotImplementedError

    def contains_err(self, error_value: E) -> bool:
        raise NotImplementedError


@final
class Ok(Result[T, E]):
    """
    Contains the success value of a computation.
    """

    __slots__ = ("_value", "is_ok", "is_err")

    def __init__(self, value: T) -> None:
        self._value = value
        self.is_ok = True
        self.is_err = False

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ok) and self._value == other._value

    def ok(self) -> Optional[T]:
        return self._value

    def err(self) -> Optional[E]:
        return None

    def map(self, op: Callable[[T], U]) -> "Result[U, E]":
        return Ok(op(self._value))

    def map_err(self, op: Callable[[E], F]) -> "Result[T, F]":
        return cast("Result[T, F]", self)

    def and_then(self, op: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return op(self._value)

    def or_else(self, op: Callable[[E], "Result[T, F]"]) -> "Result[T, F]":
        return cast("Result[T, F]", self)

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> E:
        raise Exception(f"Called `unwrap_err()` on an `Ok` value: {self._value!r}")

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self._value

    def contains(self, value: T) -> bool:
        return self._value == value

    def contains_err(self, error_value: E) -> bool:
        return False


@final
class Err(Result[T, E]):
    """
    Contains the error value of a computation.
    """

    __slots__ = ("_error", "is_ok", "is_err")

    def __init__(self, error: E) -> None:
        self._error = error
        self.is_ok = False
        self.is_err = True

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Err) and self._error == other._error

    def ok(self) -> Optional[T]:
        return None

    def err(self) -> Optional[E]:
        return self._error

    def map(self, op: Callable[[T], U]) -> "Result[U, E]":
        return cast("Result[U, E]", self)

    def map_err(self, op: Callable[[E], F]) -> "Result[T, F]":
        return Err(op(self._error))

    def and_then(self, op: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return cast("Result[U, E]", self)

    def or_else(self, op: Callable[[E], "Result[T, F]"]) -> "Result[T, F]":
        return op(self._error)

    def unwrap(self) -> T:
        raise Exception(f"Called `unwrap()` on an `Err` value: {self._error!r}")

    def unwrap_err(self) -> E:
        return self._error

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self._error)

    def contains(self, value: T) -> bool:
        return False

    def contains_err(self, error_value: E) -> bool:
        return self._error == error_value


# A Result can be either Ok or Err
ResultT = Union[Ok[T, E], Err[T, E]]
