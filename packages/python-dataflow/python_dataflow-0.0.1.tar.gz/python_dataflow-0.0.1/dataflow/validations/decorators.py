from typing import Callable, Any, Type, Optional

from dataflow.mutations.types import MutationProtocol
from dataflow.validations.types import ValidationProtocol
from dataflow.validations.failure_handlers.common import warn_validation, assert_validation


def apply_common_validations(
    warn: bool,
    asserted: bool,
    validation_callback: Optional[Callable[..., Any]],
) -> Optional[Callable[..., Any]]:
    if any([warn, asserted]) and validation_callback is not None:
        raise ValueError(
            "Invalid configuration for common validation."
            "You cannot use warn=True with custom validation callbacks"
        )

    if warn:
        return warn_validation
    if asserted:
        return assert_validation
    else:
        return validation_callback


def validate(
    validation_function: Callable[..., bool],
    validation_cls: Type[ValidationProtocol],
    warn: bool = False,
    asserted: bool = False,
    skip: bool = False,
    record: bool = True,
    validation_callback: Optional[Callable[..., Any]] = None,
    hint: Optional[str] = None,
) -> Callable[[MutationProtocol], ValidationProtocol]:
    def wrapper(mutation: MutationProtocol) -> MutationProtocol | ValidationProtocol:
        nonlocal validation_callback

        if skip:
            return mutation

        validation_callback = apply_common_validations(
            warn=warn, asserted=asserted, validation_callback=validation_callback,
        )
        return validation_cls(
            validated_function=mutation,
            validation_function=validation_function,
            validation_callback=validation_callback,
            hint=hint,
            record=record,
        )

    return wrapper
