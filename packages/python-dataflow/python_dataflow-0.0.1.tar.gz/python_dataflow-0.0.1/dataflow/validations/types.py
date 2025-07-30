from typing import Protocol, Callable, Any, Optional, runtime_checkable

from dataflow.validations.dto import ValidationFail


@runtime_checkable
class ValidationProtocol(Protocol):
    hint: str | None
    record: bool
    excluded_arguments: tuple[str, ...]
    fails: list[ValidationFail]

    validated_function: Callable[..., Any]
    validation_function: Callable[..., bool]
    validation_callback: Optional[Callable[..., Any]]

    def __call__(self, **kwargs: Any) -> Any: ...
    def fail(self, **kwargs: Any) -> Any: ...
    def validate(self, **kwargs: Any) -> Any: ...
    def __str__(self) -> str: ...
