import warnings

from dataflow.validations.validations import Validation
from dataflow.validations.errors import ValidationError


def warn_validation(*_, validation: Validation, **__) -> None:
    error = ValidationError(validation=validation)
    warnings.warn(str(error), category=RuntimeWarning)


def assert_validation(*_, validation: Validation, **__) -> None:
    error = ValidationError(validation=validation)
    assert False, str(error)

