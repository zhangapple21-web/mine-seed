
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict
import time
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class Task(BaseModel):
    id: str
    payload: Dict
    priority: str = "medium"
    retries: int = 0
    max_retries: int = 3
    created_at: int = int(time.time())
    run_after: int = int(time.time())
    status: TaskStatus = TaskStatus.PENDING
    executor_id: Optional[str] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None
    failed_at: Optional[int] = None
    error: Optional[str] = None
    result: Optional[Dict] = None

    @staticmethod
    def create(payload: Dict, priority="medium", delay=0, max_retries=3):
        now = int(time.time())
        return Task(
            id=f"task-{uuid.uuid4()}",
            payload=payload,
            priority=priority,
            retries=0,
            max_retries=max_retries,
            created_at=now,
            run_after=now + delay,
            status=TaskStatus.PENDING
        )

    def mark_running(self, executor_id):
        self.status = TaskStatus.RUNNING
        self.executor_id = executor_id
        self.started_at = int(time.time())

    def mark_completed(self, result):
        self.status = TaskStatus.DONE
        self.result = result
        self.completed_at = int(time.time())

    def mark_failed(self, error_msg):
        self.status = TaskStatus.FAILED
        self.error = error_msg
        self.failed_at = int(time.time())

    def mark_timeout(self):
        self.status = TaskStatus.FAILED
        self.error = "Timeout"

    def can_retry(self):
        return self.retries < self.max_retries
