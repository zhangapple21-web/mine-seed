
import redis
import json
import time
from jos.core.task import Task

PRIORITIES = ["critical", "high", "medium", "low"]

class RedisQueue:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def enqueue(self, task: Task):
        queue_key = f"task_queue:{task.priority}"
        self.client.zadd(queue_key, {task.json(): task.run_after})
        self.client.hset("task_status", task.id, task.json())

    def pop_task(self):
        now = int(time.time())
        for priority in PRIORITIES:
            queue_key = f"task_queue:{priority}"
            tasks = self.client.zrangebyscore(queue_key, 0, now, start=0, num=1)
            if tasks:
                task_json = tasks[0]
                self.client.zrem(queue_key, task_json)
                return Task(**json.loads(task_json))
        return None

    def complete_task(self, task: Task):
        self.client.hset("task_status", task.id, task.json())

    def fail_task(self, task: Task, reason: str):
        self.client.hset("task_status", task.id, task.json())

    def requeue_task(self, task: Task):
        task.retries += 1
        task.status = "retrying"
        self.enqueue(task)

    def update_status(self, task_id, status):
        record = self.client.hget("task_status", task_id)
        if record:
            task_data = json.loads(record)
            task_data["status"] = status
            self.client.hset("task_status", task_id, json.dumps(task_data))

    def get_all_statuses(self):
        raw = self.client.hgetall("task_status")
        return {k: json.loads(v) for k, v in raw.items()}
