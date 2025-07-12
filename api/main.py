from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr, Field
import logging
import grpc
from output import auth_pb2, auth_pb2_grpc, task_pb2, task_pb2_grpc
from typing import Dict
from google.protobuf.empty_pb2 import Empty
from typing import List
from typing import Any

class Task(BaseModel):
    task_id: str
    task_name: str
    task_description: str

class User(BaseModel):
    id: str  # changed from int to str
    email: EmailStr
    full_name: str
    avatar_url: str = None

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    avatar_url: str = None

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str= Field(min_length=6)

class TaskRequest(BaseModel): 
    task_name: str= Field(min_length=3)
    task_description: str= Field(min_length=3)

class DeleteTaskRequest(BaseModel):
    task_id: str

class DeleteTaskResponse(BaseModel):
    task_id: str
    task_name: str
    task_description: str

class GetTasksRequest(BaseModel):
    Empty   

class GetTasksResponse(BaseModel):
    tasks: List[Task]


class RegisterResponse(BaseModel):
    access_token: str
    user: User

class LoginResponse(BaseModel):
    access_token: str
    user: User

class CreateTaskResponse(BaseModel):
    task_id: str
    task_name: str
    task_description: str

class GetTaskRes(BaseModel):
    task: Task

class UpdateTaskRequest(BaseModel):
    task_name: str
    task_description: str

class UpdateTaskResponse(BaseModel):
    task_id: str
    task_name: str
    task_description: str


app = FastAPI()

SECRET_KYE='alaa_ahmade'
ALGORITHM = "HS256"

AUTH_CHANNEL = grpc.insecure_channel("localhost:50051")
TASK_CHANNEL = grpc.insecure_channel("localhost:50052")

stub = auth_pb2_grpc.AuthServiceStub(AUTH_CHANNEL)
task_stub=task_pb2_grpc.TasksServiceStub(TASK_CHANNEL)

@app.post("/register", response_model=RegisterResponse)
def register_user(user: RegisterUserRequest):
    grpc_request = auth_pb2.RegisterRequest(
      email=user.email,
      password=user.password,
      full_name=user.full_name,
      avatar_url=user.avatar_url or ""
    )
    try:
        grpc_response = stub.Register(grpc_request)

        return RegisterResponse(
            access_token=grpc_response.access_token,
            user=User(
                id=grpc_response.user.id,
                email=grpc_response.user.email,
                full_name=grpc_response.user.full_name,
                avatar_url=grpc_response.user.avatar_url
            )
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail="User already exists")
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        import traceback
        print("Exception in register_user:", e, flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login", response_model=LoginResponse)
def login(user: LoginUserRequest):
    grpc_request = auth_pb2.LoginRequest(
        email=user.email,
        password=user.password
    )
    try:
        grpc_response = stub.Login(grpc_request)

        return LoginResponse(
            access_token=grpc_response.access_token,
            user=User(
                id=grpc_response.user.id,
                email=grpc_response.user.email,
                full_name=grpc_response.user.full_name,
                avatar_url=grpc_response.user.avatar_url
            )
        )
    except grpc.RpcError as e:
        print("gRPC code:", e.code())
        print("gRPC details:", e.details())
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail="User already exists")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        import traceback
        print("Exception in login:", e, flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post('/tasks', response_model=CreateTaskResponse)
def createTask(task: TaskRequest):
    grpc_request = task_pb2.CreateTaskRequest(
        task_name=task.task_name,
        task_description=task.task_description
    )
    try:
        grpc_response = task_stub.CreateTask(
            grpc_request
        )
        return CreateTaskResponse(
           task_id=grpc_response.task_id,
           task_name=grpc_response.task_name,
           task_description=grpc_response.task_description
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail="Task already exists with same name.")
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        import traceback
        print("Exception in createTask:", e, flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
        
@app.get("/tasks", response_model=GetTasksResponse)
def getTasks():
   grpc_req = task_pb2.GetTasksReq()
   try:
        grpc_res = task_stub.GetTasks(grpc_req)
        # Convert protobuf Task messages to dicts
        tasks = [
            Task(
                task_id=task.task_id,
                task_name=task.task_name,
                task_description=task.task_description
            )
            for task in grpc_res.tasks
        ]
        return GetTasksResponse(tasks=tasks)
   except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Task not found")
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/tasks/{task_id}", response_model=DeleteTaskResponse)
def deleteTask(task_id: str):
    grpc_req = task_pb2.DeleteTaskReq(task_id=task_id)
    try:
        grpc_res = task_stub.DeleteTask(grpc_req)
        return DeleteTaskResponse(
           task_id=grpc_res.task.task_id,
           task_name=grpc_res.task.task_name,
           task_description=grpc_res.task.task_description
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Task not found")
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks/{task_id}", response_model=GetTaskRes)
def getTask(task_id: str):
    grpc_req = task_pb2.GetTaskReq(
        task_id=task_id
    )
    try:
        grpc_res = task_stub.GetTask(grpc_req)
        return GetTaskRes(
            task=Task(
                task_id=grpc_res.task.task_id,
                task_name=grpc_res.task.task_name,
                task_description=grpc_res.task.task_description
            )
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Task not found")
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/tasks/{task_id}", response_model=UpdateTaskResponse)
def updateTask(task_id: str, task: UpdateTaskRequest):
    grpc_req = task_pb2.UpdateTaskReq(
        task_id=task_id,
        task_name=task.task_name,
        task_description=task.task_description
    )
    try:
        grpc_res = task_stub.UpdateTask(grpc_req)
        return UpdateTaskResponse(
           task_id=grpc_res.task_id,
           task_name=grpc_res.task_name,
           task_description=grpc_res.task_description
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Task not found")
        print(e.details())
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        import traceback
        print("Exception in updateTask:", e, flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
