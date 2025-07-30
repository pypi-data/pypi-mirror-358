import asyncio
import json
import time
from pathlib import Path
from statistics import median
from typing import List, Dict, Any

from loguru import logger

from pydhara import SYSTEM_COMMAND_TOPIC, SystemCommand
from pydhara.core.operator import Operator


class JsonStreamer(Operator):
    json_path: Path
    data: List[Dict]

    async def pre_start(self):
        print(self.configurations)
        self.data = json.loads(Path(self.configurations["json_path"]).read_text())
        logger.debug(f"Json loaded with {len(self.data)} entries")

    async def processor(self):
        """to be called individually if the operator requires independent initialization"""
        await asyncio.sleep(3)
        start_time = time.perf_counter()
        for entry in self.data:
            await self._task_running_signal.wait()
            entry["timestamp"] = time.perf_counter()
            await self.publish(entry, topic="events")
            await asyncio.sleep(1e-15)
            # await asyncio.sleep(1e-7)
        end_time = time.perf_counter()

        logger.warning(f"Data sending completed in {end_time - start_time}s, Terminate all signal will be propagated in 5 seconds")
        # await asyncio.sleep(5)
        await self.publish(topic=SYSTEM_COMMAND_TOPIC, data=SystemCommand.TERMINATE_ALL.value)


class JsonSink(Operator):
    json_save_path: Path
    data: List[Dict]

    async def pre_start(self):
        self.data = []

    async def process_new_message(self, data: Any, topic: str):
        data["received_timestamp"] = time.perf_counter()
        self.data.append(data)
        return data

    async def post_stop(self):
        latencies = []
        min_timestamp = min([d["timestamp"] for d in self.data])
        max_timestamp = max([d["timestamp"] for d in self.data])
        min_received_timestamp = min([d["received_timestamp"] for d in self.data])
        max_received_timestamp = max([d["received_timestamp"] for d in self.data])

        mismatch_in_sequence = 0

        for i in range(len(self.data)):
            d = self.data[i]
            latency = d["received_timestamp"] - d["timestamp"]
            latencies.append(latency)
            self.data[i]["latency_sec"] = latency

            if i > 1:
                if self.data[i]['index'] < self.data[i - 1]['index']:
                    mismatch_in_sequence += 1

        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = sum(latencies) / len(latencies)
        median_latency = median(latencies)

        Path(self.configurations["json_save_path"]).write_text(json.dumps(self.data))

        print(f"total messages received: {len(self.data)} in {max_received_timestamp - min_timestamp}")
        print()
        print(f"min_timestamp: {min_timestamp}")
        print(f"max_timestamp: {max_timestamp}")
        print()
        print(f"min_received_timestamp: {min_received_timestamp}")
        print(f"max_received_timestamp: {max_received_timestamp}")
        print()
        print(f"min_latency: {min_latency}")
        print(f"max_latency: {max_latency}")
        print(f"avg_latency: {avg_latency}")
        print(f"median_latency: {median_latency}")
        print()
        print(f"speed: {len(latencies) / (max_received_timestamp - min_timestamp)} messages per sec")
        print()
        print(f"total sequence mismatches: {mismatch_in_sequence}")
