from typing import Callable, Any

from dataflow.mutations import Mutation
from dataflow.mutations.types import ReturnT
from dataflow.mutations.creators import MutationCreator


def mutation(mutation_cls: type[Mutation] | None = None) -> Callable[
    [Callable[..., ReturnT]], MutationCreator[Any, ReturnT],
]:
    def decorator(
        mutation_function: Callable[..., ReturnT],
    ) -> MutationCreator[Any, ReturnT]:
        return MutationCreator(
            name=mutation_function.__name__,
            mutation_function=mutation_function,
            mutation_cls=mutation_cls or Mutation,
        )

    return decorator
