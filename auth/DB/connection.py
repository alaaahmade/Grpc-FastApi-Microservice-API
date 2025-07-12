from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.models.user import Base
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


Base.metadata.create_all(bind=engine)