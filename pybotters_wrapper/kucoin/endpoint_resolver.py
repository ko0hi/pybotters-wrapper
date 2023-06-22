import pybotters


class KuCoinEndpointResolver:

    def __init__(self, client: pybotters.Client, exchange: str):
        from pybotters_wrapper.factory import create_factory

        self._client = create_factory(exchange).create_api_client(client)
        self._exchange = exchange
        self._data: dict | None = None

    def resolve(self, revalidate: bool = False) -> str:
        if self._data is None or revalidate:
            self._data = self._fetch_data()
        return self._get_endpoint()

    def _fetch_data(self) -> dict:
        resp = self._client.spost("/api/v1/bullet-private")
        if resp.status_code == 400:
            resp = self._client.spost("/api/v1/bullet-public")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch token: {resp.text}")
        data = resp.json()
        return data["data"]

    def _get_endpoint(self) -> str:
        assert self._data is not None
        return pybotters.KuCoinDataStore._create_endpoint(self._data)
