"""
Task routes: full CRUD, scoped to the authenticated user.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.service import TaskService, TaskNotFoundError
from app.core.models import User, TaskStatus, TaskPriority
from app.api.schemas import TaskCreate, TaskUpdate, TaskOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return service.create_task(owner_id=user.id, **payload.model_dump())


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status_filter: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return service.list_tasks(owner_id=user.id, status=status_filter, priority=priority)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    try:
        return service.get_task(task_id, owner_id=user.id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    try:
        return service.update_task(task_id, owner_id=user.id, **payload.model_dump(exclude_unset=True))
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/done", response_model=TaskOut)
def mark_done(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    try:
        return service.mark_done(task_id, owner_id=user.id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = TaskService(db)
    try:
        service.delete_task(task_id, owner_id=user.id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
