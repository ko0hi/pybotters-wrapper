import pytest

from pybotters_wrapper.plugins._base import Plugin
from pybotters_wrapper.plugins.mixins import PublishQueueMixin


def test_public_queue_mixin_w_init():
    class Hoge(Plugin, PublishQueueMixin):
        def __init__(self):
            super(Hoge, self).__init__()
            self.init_publish_queue()
    p = Hoge()
    p.subscribe()
    p.put(1)


def test_public_queue_mixin_wo_init():
    class Hoge(Plugin, PublishQueueMixin):
        def __init__(self):
            super(Hoge, self).__init__()

    p = Hoge()
    with pytest.raises(RuntimeError):
        p.subscribe()

    with pytest.raises(RuntimeError):
        p.put(1)
