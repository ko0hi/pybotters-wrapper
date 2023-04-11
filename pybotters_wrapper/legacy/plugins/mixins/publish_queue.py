import asyncio

from .helper import generate_attribute_checker


class PublishQueueMixin:
    # インスタンス変数は必ず__で宣言。さもないと異なるmixinクラスが異なるオブジェクトを
    # 同じインスタンス変数名で取ると意図せず上書きする。
    __queues: list[asyncio.Queue]
    __checker = generate_attribute_checker("init_publish_queue",
                                           "_PublishQueueMixin__queues")

    def init_publish_queue(self):
        self.__queues = []

    @__checker
    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.__queues.append(q)
        return q

    @__checker
    def put(self, item: any):
        for q in self.__queues:
            q.put_nowait(item)
