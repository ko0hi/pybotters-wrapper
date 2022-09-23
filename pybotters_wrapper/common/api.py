import pybotters


class API:
    BASE_URL = None

    def __init__(self, client: pybotters.Client):
        self._client = client

    async def request(self, method, url, *, params=None, data=None, **kwargs):
        url = self._attach_base_url(url)
        return self._client.request(method, url, params=params, data=data, **kwargs)

    async def get(self, url, *, params=None, data=None, **kwargs):
        return self.request("GET", url, params=params, data=data, **kwargs)

    async def post(self, url, *, params=None, data=None, **kwargs):
        return self.request("POST", url, params=params, data=data, **kwargs)

    async def market_order(self, symbol, side, size, **kwargs):
        raise NotImplementedError

    async def limit_order(self, symbol, side, size, price, **kwargs):
        raise NotImplementedError

    async def cancel_order(self, **kwargs):
        raise NotImplementedError

    def _attach_base_url(self, url):
        if self._client._base_url is None:
            return self.BASE_URL + url
        else:
            return url
