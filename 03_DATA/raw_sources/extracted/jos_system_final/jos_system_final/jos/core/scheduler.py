
import asyncio
from jos.queue.redis_queue import RedisQueue
from jos.executor.executor import execute_task
from jos.core.task import TaskStatus

class Scheduler:
    def __init__(self):
        self.queue = RedisQueue()
        self.running = True

    async def run(self):
        print("[🚀] Scheduler started")
        while self.running:
            task = self.queue.dequeue()
            if task:
                print(f"[▶️] Dispatching task: {task.id}")
                self.queue.update_status(task.id, TaskStatus.RUNNING)
                try:
                    result = await execute_task(task)
                    self.queue.update_status(task.id, TaskStatus.DONE)
                    print(f"[✅] Done: {task.id}")
                except Exception as e:
                    if task.retries < task.max_retries:
                        task.retries += 1
                        self.queue.enqueue(task)
                        self.queue.update_status(task.id, TaskStatus.RETRYING)
                        print(f"[🔁] Retry: {task.id}")
                    else:
                        self.queue.update_status(task.id, TaskStatus.FAILED)
                        print(f"[❌] Failed: {task.id}")
            await asyncio.sleep(0.5)
