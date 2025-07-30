from __future__ import annotations

from typing import Callable, Any, Optional, Generic, cast

from dataflow.utils import ArgumentParser
from dataflow.validations.validations import Validation
from dataflow.mutations.formatters.common import DictFormatter
from dataflow.mutations.formatters.dto import CompletedPipeline
from dataflow.mutations.types import DataT, ReturnT, MutationCallbackProtocol
from dataflow.mutations.formatters.types import MutationFormatterProtocol


class Mutation(Generic[DataT, ReturnT]):
    def __init__(
        self,
        name: str,
        mutation_function: Callable[..., ReturnT],
        context: dict[str, Any],
        default_formatter: type[MutationFormatterProtocol] = DictFormatter,
    ) -> None:
        self.name = name
        self.context = dict(context)
        self.subscribers: list[MutationCallbackProtocol] = []
        self.previous: Optional[Mutation[Any, DataT]] = None
        self.mutation_function = mutation_function
        self.default_formatter = default_formatter()

    @property
    def validations(self) -> list[Validation]:
        current_function = self.mutation_function
        validations = []

        while isinstance(current_function, Validation):
            validations.append(current_function)
            current_function = current_function.validated_function

        return validations

    @property
    def chain(self) -> list[Mutation]:
        mutations_chain = []
        current_mutation = self

        while current_mutation.previous is not None:
            mutations_chain.append(current_mutation)
            current_mutation = current_mutation.previous

        mutations_chain.append(current_mutation)
        return list(reversed(mutations_chain))

    def subscribe(self, callback: MutationCallbackProtocol) -> None:
        if self.previous is not None:
            self.previous.subscribe(callback=callback)

        self.subscribers.append(callback)

    def unsubscribe(self, callback: MutationCallbackProtocol) -> None:
        if self.previous is not None:
            self.previous.subscribe(callback=callback)

        self.subscribers.remove(callback)

    def mutate(self, **kwargs: Any) -> ReturnT:
        parser = ArgumentParser(kwargs=kwargs)

        for mutation in self.chain:
            parser = ArgumentParser(kwargs=kwargs)
            data = mutation.mutation_function(**kwargs, **mutation.context)
            kwargs = parser.parse(kwargs=kwargs, data=data)

            for callback in self.subscribers:
                callback(name=mutation.name, data=data, context=mutation.context)

        return parser.parse_return(kwargs=kwargs)

    def dumps(self, formatter: MutationFormatterProtocol | None = None) -> Any:
        formatter = formatter or self.default_formatter
        return formatter.dumps(mutations=cast(list, self.chain))

    def loads(
        self, data: Any, formatter: MutationFormatterProtocol | None = None
    ) -> CompletedPipeline:
        formatter = formatter or self.default_formatter
        return formatter.loads(data=data)

    def __rshift__(
        self, previous_mutation: Mutation[Any, DataT]
    ) -> Mutation[DataT, ReturnT]:
        previous_mutation.previous = self
        return previous_mutation

    def __call__(self, **kwargs: Any) -> ReturnT:
        return self.mutate(**kwargs)

    def __str__(self) -> str:
        mutations = []

        for mutation in self.chain:
            context = ", ".join(
                f"{key}={value!r}" for key, value in mutation.context.items()
            )
            mutations.append(f"{mutation.name}({context})")

        return " >> ".join(reversed(mutations))
