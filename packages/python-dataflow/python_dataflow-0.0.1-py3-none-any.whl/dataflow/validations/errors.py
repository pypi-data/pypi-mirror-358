from dataflow.validations.types import ValidationProtocol


class ValidationError(ValueError):
    def __init__(self, validation: ValidationProtocol):
        super().__init__()
        self.validation = validation

    def __str__(self):
        return f"{self.validation} failed"
