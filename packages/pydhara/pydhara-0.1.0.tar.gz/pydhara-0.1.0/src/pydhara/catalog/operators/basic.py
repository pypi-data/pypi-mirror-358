import asyncio
from typing import Any

from loguru import logger

from pydhara import SYSTEM_COMMAND_TOPIC, SystemCommand
from pydhara.core.operator import Operator


class IncrementingTickGenerator(Operator):
    count: int = 0

    async def processor(self):
        """to be called individually if the operator requires independent initialization"""
        self.count = 0
        await asyncio.sleep(3)
        while self.count < 10:
            await self._task_running_signal.wait()
            await self.publish(self.count, topic="integers")
            await self.publish(-self.count, topic="negative-integers")
            logger.info(f"publishing {self.count} complete")
            self.count += 1
            await asyncio.sleep(0.1)
        await self.publish(topic=SYSTEM_COMMAND_TOPIC, data=SystemCommand.TERMINATE_ALL)


class DataPrintOperator(Operator):

    async def process_new_message(self, data: Any, topic: str):
        logger.info(f"DataPrintOperator - {topic}: {data}")
        return None
