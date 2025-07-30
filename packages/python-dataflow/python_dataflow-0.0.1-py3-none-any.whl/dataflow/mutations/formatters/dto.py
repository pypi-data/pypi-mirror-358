from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from dataflow.validations.dto import ValidationFail


@dataclass
class CompletedValidationData:
    name: str
    fails: list[ValidationFail]


@dataclass
class CompletedMutationData:
    name: str
    context: dict[str, Any]
    validations: list[CompletedValidationData]


@dataclass
class CompletedPipeline:
    id: UUID
    pipeline_sequence: UUID
    pipeline: list[CompletedMutationData]
    pipeline_name: Optional[str] = None
