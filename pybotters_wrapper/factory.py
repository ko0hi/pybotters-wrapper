import pybotters


def create_client(
    apis: dict[str, list[str]] | str | None = None,
    base_url: str = "",
    **kwargs: any,
) -> pybotters.Client:
    return pybotters.Client(apis, base_url, **kwargs)
