import time
from threading import Thread
from multiprocessing import Process

import zmq
import zmq.asyncio
from zmq.asyncio import Context

MSGS = 20
PRODUCERS = 2


async def produce(url, ident):
    """Produce messages"""
    ctx = Context()
    # ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PUB)
    s.connect(url)
    print(f"Producing {ident}")
    topics = ['a', 'b', 'c', 'd']
    for i in range(1, MSGS+1):
        await s.send_multipart([f'{topics[i%len(topics)]}'.encode(), f"{ident}: {time.time():.0f}".encode()])
        # await s.send_multipart(["a".encode(), "b".encode(), f'{ident}: {time.time():.0f}'.encode()])
        # await s.send_multipart(["ab".encode(), "b".encode(), f'{ident}: {time.time():.0f}'.encode()])
        await asyncio.sleep(0.0001)

    await s.send_multipart(['system'.encode(), 'end'.encode()])
    print(f"Producer {ident} done")
    s.close()


async def consume(url, name, topic=""):
    """Consume messages"""
    ctx = Context()
#     ctx = zmq.Context.instance()
    s = ctx.socket(zmq.SUB)
    s.connect(url)
    s.setsockopt_string(zmq.SUBSCRIBE, topic)
    s.setsockopt_string(zmq.SUBSCRIBE, "system")
    print(f"Consuming {name}")
    ends = PRODUCERS
    while ends:
        topic, msg = await s.recv_multipart()
        print(f"consumer-{name}: {topic.decode()} -> {msg.decode()}")
        if topic.decode() == "system":
            if msg.decode() == "end":
                ends -= 1
    print(f"Consumer {name} done")
    s.close()


async def capture(url, name, topic=""):
    """Consume messages"""
    ctx = Context()
#     ctx = zmq.Context.instance()
    s = ctx.socket(zmq.SUB)
    s.connect(url)
    s.setsockopt_string(zmq.SUBSCRIBE, topic)
    s.setsockopt_string(zmq.SUBSCRIBE, "system")
    print(f"Consuming {name}")
    ends = PRODUCERS
    while ends:
        data = await s.recv_multipart()
        print(f"consumer-{name}: {data}")
        # if isinstance(data, str) or isinstance(data, bytes):
        #     print(f"consumer-{name}: {data.decode()}")
        #     if "end" in data.decode():
        #         ends -= 1
        # else:
        #     topic, msg = data
        #     print(f"consumer-{name}: {topic.decode()} -> {msg.decode()}")
        #     if topic.decode() == "system":
        #         if msg.decode() == "end":
        #             ends -= 1


    print(f"Consumer {name} done")
    s.close()



async def proxy(in_url, out_url, capture_url=None):
    ctx = Context()
    in_s = ctx.socket(zmq.XSUB)
    in_s.bind(in_url)

    out_s = ctx.socket(zmq.XPUB)
    out_s.bind(out_url)

    if capture_url:
        cap_s = ctx.socket(zmq.PUB)
        cap_s.bind(capture_url)
    else:
        cap_s = None
    try:
        print("proxy started")
        zmq.proxy(in_s, out_s, cap_s)
        print("proxy ended")
    except zmq.ContextTerminated:
        print("proxy terminated")
        in_s.close()
        out_s.close()


import asyncio
from concurrent.futures import ProcessPoolExecutor

async def hello():
    for i in range(10):
        print(f"hello - {i}")

def runner(fn, *args):
    asyncio.run(fn(*args))


async def main():
    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor()

    in_url = 'tcp://127.0.0.1:5555'
    out_url = 'tcp://127.0.0.1:5556'
    cap_url = 'tcp://127.0.0.1:5557'

    tasks = []

    # proxy_thread
    proxy_task = loop.run_in_executor(executor, runner, proxy, in_url, out_url, cap_url)

    # consumer
    tasks.extend([loop.run_in_executor(executor, runner, consume, out_url, i, i) for i in ["a"]])
    # tasks.extend([loop.create_task(consume(out_url, i, i)) for i in ['a', 'b', 'c']])

    capture_task = loop.run_in_executor(executor, runner, capture, cap_url, "capture", "")

    await asyncio.sleep(2)

    # producers
    tasks.extend([loop.run_in_executor(executor, runner, produce, in_url, i) for i in range(PRODUCERS)])

    # tasks = [loop.run_in_executor(executor, runner, hello) for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)
    proxy_task.cancel()
    # await proxy_task

    capture_task.cancel()
    # await capture_task

    executor.shutdown(wait=False)

if __name__ == '__main__':
    # Run the main function
    asyncio.run(main())