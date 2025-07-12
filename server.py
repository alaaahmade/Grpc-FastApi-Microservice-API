import grpc
from concurrent import futures
from auth.service import AuthService
from tasks.service import TasksService
from output import auth_pb2_grpc, task_pb2_grpc
import threading

def auth():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    print("AuthService gRPC server running on http://localhost:50051")
    server.start()
    server.wait_for_termination()

def task():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_pb2_grpc.add_TasksServiceServicer_to_server(TasksService(), server)
    server.add_insecure_port('[::]:50052')
    print("TasksService gRPC server running on http://localhost:50052")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    t1 = threading.Thread(target=auth)
    t2 = threading.Thread(target=task)
    t1.start()
    t2.start()
    t1.join()
    t2.join()