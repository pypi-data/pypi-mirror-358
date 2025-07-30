import functools
from typing import Any, Callable

from dataflow.utils import ArgumentParser
from dataflow.validations.validations import Validation
from dataflow.validations.decorators import validate, MutationProtocol


class AfterValidation(Validation):
    def validate(self, **kwargs: Any) -> Any:
        result = self.validated_function(**kwargs)

        parser = ArgumentParser(kwargs=kwargs)
        parsed_kwargs = parser.parse(kwargs=kwargs, data=result)

        if not self.validation_function(**{**kwargs, **parsed_kwargs}):
            self.fail(**kwargs)

        return result


after: Callable[..., Callable[[MutationProtocol], AfterValidation]] = functools.partial(
    validate,
    validation_cls=AfterValidation,
)
