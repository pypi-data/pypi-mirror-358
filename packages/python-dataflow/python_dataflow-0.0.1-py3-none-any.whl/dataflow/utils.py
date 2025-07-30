from typing import Any


class ArgumentParser:
    def __init__(self, kwargs: dict[str, Any]):
        self.argument_key = list(kwargs.keys())[0] if len(kwargs) == 1 else None

    def parse(self, kwargs: dict[str, Any], data: Any) -> dict[str, Any]:
        if self.argument_key is not None:
            kwargs[self.argument_key] = data
        elif data is not None and isinstance(data, dict):
            kwargs = data

        return kwargs

    def parse_return(self, kwargs: dict[str, Any]) -> Any:
        if self.argument_key is None:
            return kwargs

        return kwargs[self.argument_key]
