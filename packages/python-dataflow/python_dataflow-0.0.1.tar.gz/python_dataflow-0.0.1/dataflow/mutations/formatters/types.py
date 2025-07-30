from typing import Protocol, TypeVar

from dataflow.mutations.formatters.dto import CompletedPipeline
from dataflow.mutations.types import MutationProtocol


FormattedT = TypeVar("FormattedT")


class MutationFormatterProtocol(Protocol[FormattedT]):
    def dumps(self, mutations: list[MutationProtocol]) -> FormattedT: ...

    def loads(self, data: FormattedT) -> CompletedPipeline: ...
