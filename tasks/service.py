from output import task_pb2, task_pb2_grpc
from tasks.DB.connection import SessionLocal
from sqlalchemy import select
from tasks.models.task import Task as DBTask
from uuid import uuid4
import grpc


SECRET_KEY = "alaa_ahmade"
ALGORITHM = "HS256"

class TasksService(task_pb2_grpc.TasksService):
  def CreateTask(self, request, context):
    db = SessionLocal()
    try:
      # Input validation
      if not request.task_name or not request.task_description:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "task_name and task_description are required.")
      existing = db.query(DBTask).filter(DBTask.task_name == request.task_name).first()
      if existing:
        context.abort(grpc.StatusCode.ALREADY_EXISTS, "Task already exists with the same name!")
      task_id = str(uuid4())
      task = DBTask(
        task_id=task_id,
        task_name=request.task_name,
        task_description=request.task_description
      )
      db.add(task)
      db.commit()
      db.refresh(task)
      resp = task_pb2.CreateTaskResponse(
        task_id=task_id,
        task_name=task.task_name,
        task_description=task.task_description
      )
      return resp
    finally:
      db.close()

  def GetTasks(self, request, context):
    db = SessionLocal()
    try:
      db_tasks = db.query(DBTask).all()
      resp = [
        task_pb2.Task(
          task_id=task.task_id,
          task_name=task.task_name,
          task_description=task.task_description
        )
        for task in db_tasks
      ]
      return task_pb2.GetTasksRes(tasks=resp)
    finally:
      db.close()

  def DeleteTask(self, req, con):
    db = SessionLocal()
    try:
      # Input validation
      if not getattr(req, 'task_id', None):
        con.abort(grpc.StatusCode.INVALID_ARGUMENT, "task_id is required.")
      db_task = db.get(DBTask, req.task_id)
      if not db_task:
        con.abort(grpc.StatusCode.NOT_FOUND, "Task not found.")
      deleted_task = task_pb2.Task(
        task_id=db_task.task_id,
        task_name=db_task.task_name,
        task_description=db_task.task_description
      )
      db.delete(db_task)
      db.commit()
      return task_pb2.DeleteTaskRes(task=deleted_task)
    finally:
      db.close()

  def GetTask(self, req, con):
    db = SessionLocal()
    try:
      # Input validation
      if not getattr(req, 'task_id', None):
        con.abort(grpc.StatusCode.INVALID_ARGUMENT, "task_id is required.")
      task = db.get(DBTask, req.task_id)
      if not task:
        con.abort(grpc.StatusCode.NOT_FOUND, "Task not found.")
      g_task = task_pb2.Task(
        task_id=task.task_id,
        task_name=task.task_name,
        task_description=task.task_description
      )
      return task_pb2.GetTaskRes(task=g_task)

    finally:
      db.close()

  def UpdateTask(self, req, con):
    db = SessionLocal()
    try:
      # Input validation
      if not getattr(req, 'task_id', None):
        con.abort(grpc.StatusCode.INVALID_ARGUMENT, "task_id is required.")
      db_task = db.get(DBTask, req.task_id)
      if not db_task:
        con.abort(grpc.StatusCode.NOT_FOUND, "Task not found.")
      # Update fields if provided
      if req.task_name:
        db_task.task_name = req.task_name
      if req.task_description:
        db_task.task_description = req.task_description
      db.commit()
      db.refresh(db_task)
      return task_pb2.UpdateTaskRes(
        task_id=db_task.task_id,
        task_name=db_task.task_name,
        task_description=db_task.task_description
      )
    finally:
      db.close()
