import asyncio

import pybotters_wrapper as pbw


async def main():
    async with pbw.create_client() as client:
        store = pbw.create_gmocoin_store()
        await store.initialize([("position", {"symbol": "BTC_JPY"})], client)
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
