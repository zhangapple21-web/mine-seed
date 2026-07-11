
import asyncio
import random

async def execute_task(task):
    # Simulate workload
    await asyncio.sleep(random.uniform(0.5, 1.5))
    if random.random() < 0.9:
        return {"result": "success"}
    else:
        raise Exception("Simulated execution failure")
