# Microservice API with gRPC and FastAPI

## What is gRPC?

gRPC is a high-performance, open-source universal RPC (Remote Procedure Call) framework developed by Google. It uses Protocol Buffers for data serialization and supports multiple programming languages. gRPC enables efficient communication between microservices, with features like authentication, load balancing, and bidirectional streaming.

**Key features:**
- Strongly typed contracts via Protocol Buffers
- HTTP/2 transport for multiplexing and streaming
- Language-agnostic (supports many languages)
- Efficient and fast communication

## What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It is designed for speed, easy validation, and automatic interactive documentation (Swagger/OpenAPI).

**Key features:**
- Automatic data validation and documentation
- Asynchronous support for high performance
- Easy integration with Python type hints
- Great developer experience

## How to Run the Server and Service

This project uses a Makefile to simplify running and managing the gRPC service and FastAPI server.

### Prerequisites

- Python 3.12+
- `pip` for installing dependencies
- Make (Linux/macOS or Windows with WSL)

### Setup

1. Install dependencies:
   ```bash
   make install
   ```

2. Generate gRPC code from `.proto` files:
   ```bash
   make proto
   ```

### Running Services

- **Start the gRPC service:**
  ```bash
  make grpc
  ```
  This command runs the gRPC server that handles core business logic and communicates using Protocol Buffers.

- **Start the FastAPI server:**
  ```bash
  make api
  ```
  This command runs the FastAPI application, which acts as an HTTP gateway, exposing REST endpoints and communicating with the gRPC service.

### Makefile Commands Explained

- `make install`: Installs all required Python packages from `requirements.txt`.
- `make proto`: Compiles `.proto` files to generate Python gRPC code.
- `make grpc`: Starts the gRPC microservice server.
- `make api`: Starts the FastAPI HTTP API server.
- `make clean`: Removes generated files and build artifacts.

## Example Usage

1. Register a user via FastAPI:
   ```
   POST /register
   {
     "email": "user@example.com",
     "password": "securepassword",
     "full_name": "User Name"
   }
   ```

2. Create a task via FastAPI:
   ```
   POST /tasks
   {
     "task_name": "My Task",
     "task_description": "Task details"
   }
   ```

3. Update, delete, and get tasks using the respective endpoints.

## Notes

- Ensure both the gRPC and FastAPI servers are running for full functionality.
- See the interactive API docs at `http://localhost:8000/docs` when FastAPI is running.

---
