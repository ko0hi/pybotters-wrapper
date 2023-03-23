from argparse import ArgumentParser
from loguru import logger
import asyncio
import pybotters_wrapper as pbw


class SpreadMonitor:
    def __init__(self, store: pbw.bitflyer.bitFlyerDataStoreWrapper):
        self._store = store
        self._fx_ltp = None
        self._spot_ltp = None
        self._update_task = asyncio.create_task(self._auto_update_ltps())

    def spread(self, v: float = None) -> float:
        v = v or self._fx_ltp
        return (v - self._spot_ltp) / self._spot_ltp

    def spread_orderbook(self):
        asks, bids = self._store.orderbook.sorted({"symbol": "FX_BTC_JPY"}).values()
        return {
            "ask": [{**i, "spread": self.spread(i["price"])} for i in asks],
            "bid": [{**i, "spread": self.spread(i["price"])} for i in bids],
        }

    def is_ready(self) -> bool:
        return self._spot_ltp is not None and self._fx_ltp is not None

    async def initialize(self):
        while not self.is_ready():
            logger.info("Waiting...")
            await asyncio.sleep(0.1)

    async def _auto_update_ltps(self):
        with self._store.trades.watch() as stream:
            async for change in stream:
                if change.data["symbol"] == "BTC_JPY":
                    self._spot_ltp = change.data["price"]
                elif change.data["symbol"] == "FX_BTC_JPY":
                    self._fx_ltp = change.data["price"]


async def main(args):
    async with pbw.create_client() as client:
        store = pbw.create_bitflyer_store()
        api = pbw.create_bitflyer_api(client, verbose=True)
        await store.initialize_position(client, product_code="FX_BTC_JPY")
        await store.subscribe("all", symbol="FX_BTC_JPY").subscribe(
            "all", symbol="BTC_JPY"
        ).connect(client=client, waits=["trades", "orderbook"])

        monitor = SpreadMonitor(store)
        await monitor.initialize()

        while True:
            await store.orderbook.wait()
            position = store.position.summary("FX_BTC_JPY")
            logger.info(monitor.spread())

            # 売り指値
            if (
                position["SELL_size"] == 0
                and len(store.order.find({"symbol": "FX_BTC_JPY", "side": "SELL"})) == 0
            ):
                asks = monitor.spread_orderbook()["ask"]
                for a in asks:
                    if a["spread"] > args.sell_spread:
                        await api.limit_order(
                            "FX_BTC_JPY", "SELL", a["price"], args.size
                        )
                        await asyncio.sleep(1)
                        break
            # 買い指値
            if (
                position["SELL_size"] > 0
                and len(store.order.find({"symbol": "FX_BTC_JPY", "side": "BUY"})) == 0
            ):
                bids = monitor.spread_orderbook()["bid"]
                for b in bids:
                    if b["spread"] < args.buy_spread:
                        await api.limit_order(
                            "FX_BTC_JPY", "BUY", b["price"], args.size
                        )
                        await asyncio.sleep(1)
                        break

            # 指値キャンセル
            for o in store.order.find({"symbol": "FX_BTC_JPY"}):
                ref_spread = (
                    args.sell_spread if o["side"] == "SELL" else args.buy_spread
                )
                order_spread = monitor.spread(o["price"])
                if abs(order_spread - ref_spread) > args.cancel_gap:
                    await api.cancel_order("FX_BTC_JPY", o["id"])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--size", default=0.01, type=float)
    parser.add_argument("--sell_spread", default=0.051, type=float)
    parser.add_argument("--buy_spread", default=0.049, type=float)
    parser.add_argument("--cancel_gap", default=0.0001, type=float)
    args = parser.parse_args()

    asyncio.run(main(args))
