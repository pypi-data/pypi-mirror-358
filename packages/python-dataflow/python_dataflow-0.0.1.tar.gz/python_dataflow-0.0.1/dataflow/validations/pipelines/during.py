from typing import Any, Callable, Optional, Type

from dataflow.validations.decorators import apply_common_validations
from dataflow.validations.validations import Validation
from dataflow.mutations.types import MutationProtocol


class DuringValidation(Validation):
    def __init__(
        self,
        before_validation: Callable[..., Any],
        after_validation: Callable[..., Any],
        validated_function: Callable[..., bool],
        validation_callback: Optional[Callable[..., Any]],
        derived_key: str = "derived",
        data_key: str = "data",
        hint: str | None = None,
        record: bool = True,
        excluded_arguments: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(
            hint=hint,
            record=record,
            excluded_arguments=excluded_arguments,
            validated_function=validated_function,
            validation_function=lambda: False,
            validation_callback=validation_callback,
        )
        self.before_validation = before_validation
        self.after_validation = after_validation
        self.derived_key = derived_key
        self.data_key = data_key

    def validate(self, **kwargs: Any) -> Any:
        derived = {}
        is_failed = False
        kwargs[self.derived_key] = derived

        if not self.before_validation(**kwargs):
            self.fail(**kwargs)
            is_failed = True

        data = self.validated_function(**kwargs)
        if is_failed:
            return data

        if isinstance(data, dict):
            kwargs |= data
        else:
            kwargs[self.data_key] = data

        if not self.after_validation(**kwargs):
            self.fail(**kwargs)

        return data


def during(
    before_validation: Callable[..., bool],
    after_validation: Callable[..., bool],
    validation_cls: Type[DuringValidation] = DuringValidation,
    warn: bool = False,
    skip: bool = False,
    record: bool = True,
    validation_callback: Optional[Callable[..., Any]] = None,
    hint: Optional[str] = None,
) -> Callable[[MutationProtocol], Validation]:
    def wrapper(mutation: MutationProtocol) -> MutationProtocol | Validation:
        nonlocal validation_callback
        if skip:
            return mutation

        validation_callback = apply_common_validations(
            warn=warn, validation_callback=validation_callback,
        )
        return validation_cls(
            validated_function=mutation,
            before_validation=before_validation,
            after_validation=after_validation,
            validation_callback=validation_callback,
            hint=hint,
            record=record,
        )

    return wrapper
