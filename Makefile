.PHONY: api services help install proto grpc clean

help:
	@echo "make services  # Start gRPC backend services"
	@echo "make api       # Start FastAPI gateway (after services are running)"
	@echo "make install    # Install Python dependencies"
	@echo "make proto      # Generate gRPC code from .proto files"
	@echo "make grpc       # Run the gRPC microservice server"
	@echo "make clean      # Clean generated files and build artifacts"

api:
	uvicorn api.main:app --reload --port 8001

services:
	. venv/bin/activate && python3 server.py

services-dev:
	watchmedo auto-restart --patterns="*.py" --recursive -- python3 server.py

install:
	pip install -r requirements.txt

proto:
	python -m grpc_tools.protoc -I./proto --python_out=./output --grpc_python_out=./output ./proto/*.proto

grpc:
	python -m tasks.grpc_server

clean:
	rm -rf output/*.pyc output/__pycache__ api/__pycache__ tasks/__pycache__ *.db