from datetime import datetime
from typing import Callable, Any, Optional

from dataflow.validations.dto import ValidationFail
from dataflow.validations.errors import ValidationError


class Validation:
    def __init__(
        self,
        validated_function: Callable[..., Any],
        validation_function: Callable[..., bool],
        validation_callback: Optional[Callable[..., Any]],
        hint: str | None = None,
        record: bool = True,
        excluded_arguments: tuple[str, ...] | None = None,
    ) -> None:
        self.validation_function: Callable[..., bool] = validation_function
        self.validated_function: Callable[..., Any] = validated_function
        self.validation_callback: Optional[Callable[..., Any]] = validation_callback

        self.hint = hint
        self.record = record

        self.excluded_arguments = excluded_arguments or ("validation",)
        self.fails: list[ValidationFail] = []

    def __getattr__(self, item: str) -> Any:
        return getattr(self.validated_function, item)

    def __call__(self, **kwargs: Any) -> Any:
        return self.validate(**kwargs)

    def fail(self, **kwargs: Any) -> Any:
        if self.record:
            self.fails.append(
                ValidationFail(
                    hint=self.hint,
                    kwargs={
                        key: value
                        for key, value in kwargs.items()
                        if key not in self.excluded_arguments
                    },
                    failed_at=datetime.now(),
                )
            )

        if self.validation_callback is not None:
            kwargs["validation"] = self
            return self.validation_callback(**kwargs)

        raise ValidationError(validation=self)

    def validate(self, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __str__(self) -> str:
        if self.hint:
            return f"{self.__class__.__name__}({self.hint})"

        return f"{self.__class__.__name__}"
