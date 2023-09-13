from typing import Any, TypedDict


class ExchangeProperties(TypedDict):
    base_url: str
    exchange: str


class ExchangeProperty:
    def __init__(self, properties: ExchangeProperties):
        self._properties = properties
        self._validate()

    def _get(self, key: str) -> Any:
        if key not in self._properties:
            raise ValueError(f"Unknown key: {key}")
        return self._properties.get(key)

    @property
    def base_url(self) -> str | None:
        base_url = self._properties.get("base_url")
        assert base_url is not None
        return base_url

    @property
    def exchange(self) -> str:
        exchange = self._properties.get("exchange")
        assert exchange is not None
        return exchange

    def _validate(self):
        missing_properties = []
        for key in ExchangeProperties.__annotations__.keys():
            if key not in self._properties:
                missing_properties.append(key)
        if missing_properties:
            raise ValueError(f"Missing properties: {missing_properties}")
