class ExchangeProperty:
    def __init__(self, properties: dict[str, any]):
        self._properties = properties

    def _get(self, key: str) -> any:
        if key not in self._properties:
            raise ValueError(f"Unknown key: {key}")
        return self._properties.get(key)
    @property
    def base_url(self) -> str:
        return self._properties.get("base_url")

    @property
    def exchange(self) -> str:
        return self._properties.get("exchange")
