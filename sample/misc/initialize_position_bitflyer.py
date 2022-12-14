import asyncio

import pybotters_wrapper as pbw


async def main():
    async with pbw.create_client() as client:
        store = pbw.create_bitflyer_store()
        await store.initialize([("position", {"product_code": "FX_BTC_JPY"})], client)
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
