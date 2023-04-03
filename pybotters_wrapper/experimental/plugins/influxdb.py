from typing import Union
from pybotters_wrapper.core import DataStoreWrapper
from ._base import Plugin


class InfluxDB(Plugin):
    def __init__(
        self,
        token: str,
        org: str,
        bucket: str,
        host: str = "localhost",
        port: int = 8086,
        protocol: str = "http",
    ):
        super(Plugin, self).__init__()
        self._token = token
        self._org = org
        self._bucket = bucket
        self._host = host
        self._port = port
        self._protocol = protocol
        self.create_bucket()

    @property
    def url(self):
        return f"{self._protocol}://{self._host}:{self._port}"

    def client(
        self, sync: bool = False, **kwargs
    ) -> Union['InfluxDBClient', 'InfluxDBClientAsync']:
        from influxdb_client import InfluxDBClient
        from influxdb_client.client.influxdb_client_async import \
            InfluxDBClientAsync
        params = dict(url=self.url, token=self._token, org=self._org)
        client_cls = InfluxDBClient if sync else InfluxDBClientAsync
        return client_cls(**params, **kwargs)

    async def write_execution(
        self,
        measurement: str,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        timestamp: str,
        *,
        bucket: str = None,
        client: 'InfluxDBClientAsync' = None,
    ):
        bucket = bucket or self._bucket

        d = {
            "measurement": measurement,
            "tags": {"id": id, "symbol": symbol, "side": side},
            "fields": {"price": float(price), "size": float(size)},
            "time": timestamp,
        }
        if client is None:
            async with self.client() as client:
                await client.write_api().write(bucket, self._org, d)
        else:
            await client.write_api().write(bucket, self._org, d)

    def create_bucket(self, bucket: str = None, delete: bool = False):
        bucket = bucket or self._bucket
        with self.client(sync=True) as client:
            api = client.buckets_api()
            _bucket = api.find_bucket_by_name(bucket)
            if delete:
                if _bucket is not None:
                    api.delete_bucket(_bucket.id)
                return api.create_bucket(bucket_name=bucket)
            else:
                if _bucket is not None:
                    return _bucket
                else:
                    return api.create_bucket(bucket_name=bucket)

    async def watch_and_write_executions(
        self, store: DataStoreWrapper, measurement: str, bucket: str = None
    ):
        async with self.client() as client:
            with store.execution.watch() as stream:
                async for msg in stream:
                    d = msg.data
                    await self.write_execution(
                        measurement,
                        d["id"],
                        d["symbol"],
                        d["side"],
                        d["price"],
                        d["size"],
                        d["timestamp"],
                        bucket=bucket,
                        client=client,
                    )
