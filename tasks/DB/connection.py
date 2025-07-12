from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tasks.models.task import Base

DATABASE_URL = "postgresql://grpc:root@localhost:5432/grpc"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base.metadata.create_all(bind=engine)