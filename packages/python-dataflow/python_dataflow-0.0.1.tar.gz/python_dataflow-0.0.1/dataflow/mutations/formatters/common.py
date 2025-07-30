import json
import uuid
from typing import Any

from faker import Faker

from dataflow.mutations.types import MutationProtocol
from dataflow.validations.dto import ValidationFail
from dataflow.mutations.formatters.types import MutationFormatterProtocol, FormattedT
from dataflow.mutations.formatters.dto import CompletedPipeline, CompletedMutationData, CompletedValidationData


class DictFormatter(MutationFormatterProtocol):
    def dumps(self, mutations: list[MutationProtocol]) -> FormattedT:
        pipeline = [
            {
                "name": mutation.name,
                "context": mutation.context,
                "validations": [
                    {
                        "name": str(validation),
                        "fails": [
                            {
                                "hint": fail.hint,
                                "kwargs": fail.kwargs,
                                "failed_at": fail.failed_at,
                            }
                            for fail in validation.fails
                        ],
                    }
                    for validation in mutation.validations
                ],
            } for mutation in mutations
        ]

        pipeline_sequence = uuid.uuid5(
            namespace=uuid.NAMESPACE_OID,
            name="".join([mutation.name for mutation in mutations]),
        )
        pipeline_id = uuid.uuid4()

        return {
            "id": str(pipeline_id),
            "pipeline_sequence": str(pipeline_sequence),
            "pipeline": pipeline,
        }

    def loads(self, data: dict[str, Any]) -> CompletedPipeline:
        faker = Faker()
        faker.seed_instance(seed=data["pipeline_sequence"])

        return CompletedPipeline(
            id=data["id"],
            pipeline_sequence=data["pipeline_sequence"],
            pipeline_name=f"{faker.slug()}",
            pipeline=[
                CompletedMutationData(
                    name=mutation["name"],
                    context=mutation["context"],
                    validations=[
                        CompletedValidationData(
                            name=validation["name"],
                            fails=[
                                ValidationFail(
                                    hint=fail["hint"],
                                    kwargs=fail["kwargs"],
                                    failed_at=fail["failed_at"],
                                )
                                for fail in validation["fails"]
                            ],
                        )
                        for validation in mutation["validations"]
                    ],
                )
                for mutation in data["pipeline"]
            ],
        )


class JsonFormatter(MutationFormatterProtocol):
    formatter = DictFormatter()

    def dumps(self, mutations: list[MutationProtocol]) -> FormattedT:
        return json.dumps(self.formatter.dumps(mutations=mutations))

    def loads(self, data: FormattedT) -> CompletedPipeline:
        return self.formatter.loads(json.loads(data))
