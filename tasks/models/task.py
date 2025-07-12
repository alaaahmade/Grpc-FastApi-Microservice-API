from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
  __tablename__ = "tasks"
  task_id = Column(String, primary_key=True)
  task_name = Column(String(255), nullable=False)
  task_description = Column(String(255), nullable=False)