import asyncio
import random

import pandas
import pybotters_wrapper as pbw
from loguru import logger


async def main1():
    async with pbw.create_client() as client:
        api = pbw.create_binanceusdsm_api(client)
        # apiの場合、base_urlが自動付与されるのでurlにhost等が入らないことに注意

        params = {"symbol": "BTCUSDT"}
        # paramsは関数化でもオッケー
        params = lambda: {"symbol": random.choice(["BTCUSDT", "ETHUSDT"])}

        handler = None

        # restの返り値を加工するハンドラー
        # defaultは.jsonを呼ぶだけ
        async def custom_handler(item):
            data = await item.json()
            return {"rnd": random.random(), **data}

        handler = custom_handler

        poller = pbw.plugins.poller(
            api,
            url="/fapi/v1/premiumIndex",
            params=params,
            interval=15,  # 15秒に一回W
            history=99,  # 履歴数
            handler=handler,
        )

        queue = poller.subscribe()

        while True:
            item = await queue.get()
            logger.info(f"ITEM: {item}")
            logger.info(f"HISTORY: {poller.history}")


if __name__ == "__main__":
    asyncio.run(main1())
