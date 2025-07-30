import asyncio
from typing import Any

from loguru import logger

from pydhara.core.operator import Operator
from pydhara.zmq.pipeline import ZMQCentralPipeline
from pydhara import OPERATOR_CATALOG

@OPERATOR_CATALOG("NewDataPrintOperator")
class NDataPrintOperator(Operator):

    async def process_new_message(self, data: Any, topic: str):
        logger.info(f"======> DataPrintOperator <======== - {topic}: {data}")
        return None

async def main(sync_mode=False):
    pipeline = ZMQCentralPipeline()

    key = "dummy_candlestick_1_00_000"

    pipeline.add_new_operator("JsonStreamer", output_topics=("events",),
                              operator_kwargs=dict(configurations=dict(json_path=f"/home/mayank/PycharmProjects/pybeam-trader/tests/experiments/performance_test/{key}_entries.json")))
    pipeline.add_new_operator("JsonSink", input_topics=("events",), operator_kwargs=dict(
        configurations=dict(json_save_path=f"/home/mayank/PycharmProjects/pybeam-trader/tests/experiments/performance_test/results/{key}_entries_received.json")))

    pipeline.add_new_operator("NewDataPrintOperator", input_topics=("events",))

    await asyncio.sleep(1)

    pipeline.initialize()
    await pipeline.start()
    logger.debug("main ended")


if __name__ == "__main__":
    asyncio.run(main(False), debug=True)
    # asyncio.get_event_loop().run_until_complete(main(True))
