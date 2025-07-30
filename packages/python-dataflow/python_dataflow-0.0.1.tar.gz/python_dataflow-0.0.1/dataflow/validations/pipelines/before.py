import functools
from typing import Any, Callable

from dataflow.validations.validations import Validation
from dataflow.validations.decorators import validate, MutationProtocol


class BeforeValidation(Validation):
    def validate(self, **kwargs: Any) -> Any:
        if not self.validation_function(**kwargs):
            self.fail(**kwargs)

        return self.validated_function(**kwargs)


before: Callable[..., Callable[[MutationProtocol], BeforeValidation]] = functools.partial(
    validate,
    validation_cls=BeforeValidation,
)
