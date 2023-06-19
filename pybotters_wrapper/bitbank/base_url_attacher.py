class bitbankBaseUrlAttacher:
    _PRIVATE_ENDPOINTS = {
        "/user/assets",
        "/user/spot/order",
        "/user/spot/cancel_order",
        "/user/spot/cancel_orders",
        "/user/spot/orders_info",
        "/user/spot/active_orders",
        "/user/spot/trade_history",
        "/user/withdrawal_account",
        "/user/request_withdrawal",
        "/spot/status",
        "/spot/pairs",
    }

    def __call__(self, url: str) -> str:
        if url is not None and url in self._PRIVATE_ENDPOINTS:
            return f"https://api.bitbank.cc/v1{url}"
        else:
            return f"https://public.bitbank.cc{url}"
