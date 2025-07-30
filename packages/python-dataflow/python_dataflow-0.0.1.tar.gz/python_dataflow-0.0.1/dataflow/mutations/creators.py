from __future__ import annotations
from typing import Callable, Any, Generic

from dataflow.mutations.mutations import Mutation
from dataflow.mutations.types import DataT, ReturnT


class MutationCreator(Generic[DataT, ReturnT]):
    def __init__(
        self,
        name: str,
        mutation_function: Callable[..., ReturnT],
        mutation_cls: type[Mutation],
    ) -> None:
        self.name = name
        self.mutation_cls = mutation_cls
        self.mutation_function = mutation_function

    def __call__(self, **context: Any) -> Mutation[DataT, ReturnT]:
        return self.mutation_cls(
            name=self.name,
            mutation_function=self.mutation_function,
            context=context,
        )
