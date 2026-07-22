"""
TaskService: the single source of truth for task business logic.

Both the CLI and the REST API call into this exact same layer,
which is the whole point of the "CLI -> Production API" evolution:
we don't rewrite logic, we just add new interfaces on top of it.
"""
from typing import Optional, List
import datetime as dt

from sqlalchemy.orm import Session

from app.core.models import Task, TaskStatus, TaskPriority


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.medium,
        due_date: Optional[dt.datetime] = None,
        owner_id: Optional[int] = None,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            owner_id=owner_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: int, owner_id: Optional[int] = None) -> Task:
        query = self.db.query(Task).filter(Task.id == task_id)
        if owner_id is not None:
            query = query.filter(Task.owner_id == owner_id)
        task = query.first()
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(
        self,
        owner_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[Task]:
        query = self.db.query(Task)
        if owner_id is not None:
            query = query.filter(Task.owner_id == owner_id)
        if status is not None:
            query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        return query.order_by(Task.created_at.desc()).all()

    def update_task(self, task_id: int, owner_id: Optional[int] = None, **fields) -> Task:
        task = self.get_task(task_id, owner_id)
        for key, value in fields.items():
            if value is not None and hasattr(task, key):
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_done(self, task_id: int, owner_id: Optional[int] = None) -> Task:
        return self.update_task(task_id, owner_id, status=TaskStatus.done)

    def delete_task(self, task_id: int, owner_id: Optional[int] = None) -> None:
        task = self.get_task(task_id, owner_id)
        self.db.delete(task)
        self.db.commit()
