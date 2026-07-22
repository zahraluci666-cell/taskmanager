"""
Unit tests for TaskService — uses an in-memory SQLite DB per test.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.service import TaskService, TaskNotFoundError
from app.core.models import TaskStatus, TaskPriority


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def service(db_session):
    return TaskService(db_session)


def test_create_task(service):
    task = service.create_task(title="Write tests", priority=TaskPriority.high)
    assert task.id is not None
    assert task.status == TaskStatus.todo
    assert task.priority == TaskPriority.high


def test_list_tasks_filters_by_status(service):
    t1 = service.create_task(title="Task A")
    service.create_task(title="Task B")
    service.mark_done(t1.id)

    done_tasks = service.list_tasks(status=TaskStatus.done)
    todo_tasks = service.list_tasks(status=TaskStatus.todo)

    assert len(done_tasks) == 1
    assert len(todo_tasks) == 1
    assert done_tasks[0].title == "Task A"


def test_update_task(service):
    task = service.create_task(title="Old title")
    updated = service.update_task(task.id, title="New title", priority=TaskPriority.low)
    assert updated.title == "New title"
    assert updated.priority == TaskPriority.low


def test_delete_task(service):
    task = service.create_task(title="Temp")
    service.delete_task(task.id)
    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)


def test_get_missing_task_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.get_task(999)
