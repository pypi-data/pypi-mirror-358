import asyncio
import time
import threading

from cachetronomy.core.eviction.memory import MemoryEvictionThread
import cachetronomy.core.access_frequency as af

from tests.conftest import fake_mem


def test_memory_eviction_by_threshold(monkeypatch, dummy_cache):
    for k in ('a', 'b', 'c'):
        dummy_cache._memory._store[k] = f'data-{k}'
    af.promote_key('a')
    af.promote_key('b')
    af.promote_key('c')
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=loop.run_forever, daemon=True)
        t.start()
    with fake_mem(monkeypatch, avail_mb=10): # force a “low memory” state
        thread = MemoryEvictionThread(
            cache=dummy_cache,
            loop=loop,
            memory_cleanup_interval=0.02,
            free_memory_target=20,
        )
        thread.start()
        time.sleep(0.06) # give it time to do work
        thread.stop()
    assert len(dummy_cache._memory._store) < 3
    print(dummy_cache._memory.stats())
    assert dummy_cache._memory.stats()['evicted'] >= 1
