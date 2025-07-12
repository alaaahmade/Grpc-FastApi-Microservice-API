import os
import jwt
from uuid import uuid4
import grpc
from dotenv import load_dotenv
from passlib.context import CryptContext
from output import auth_pb2
from output import auth_pb2_grpc
from auth.DB.connection import SessionLocal
from auth.models.user import User as DBUser

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password:str):
    return pwd_context.hash(password)
    

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password) 
    


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def Register(self, request, context):
        db = SessionLocal()
        try:
            # Input validation
            if not request.email or not request.password or not request.full_name:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "email, password, and full_name are required.")
            existing = db.query(DBUser).filter(DBUser.user_email == request.email).first()
            if existing:
                context.abort(grpc.StatusCode.ALREADY_EXISTS, "User already exists.")
            user_id = str(uuid4())
            user = DBUser(
                user_id=user_id,
                user_name=request.full_name,
                user_email=request.email,
                user_password=hash_password(request.password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)
            resp = auth_pb2.LoginResponse(
                access_token=token,
                user=auth_pb2.User(
                    id=user_id,
                    email=user.user_email,
                    full_name=user.user_name,
                    avatar_url=""
                )
            )
            return resp
        finally:
            db.close()
    def Login(self, request, context):
        db = SessionLocal()
        try:
            if not request.email or not request.password:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "email and password are required.")
            existing = db.query(DBUser).filter(DBUser.user_email == request.email).first()
            if not existing:
                context.abort(grpc.StatusCode.NOT_FOUND, "User does not exist.")
            if not verify_password(request.password, existing.user_password):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid password.")
            token = jwt.encode({"user_id": existing.user_id}, SECRET_KEY, algorithm=ALGORITHM)
            resp = auth_pb2.LoginResponse(
                access_token=token,
                user=auth_pb2.User(
                    id=existing.user_id,
                    email=existing.user_email,
                    full_name=existing.user_name,
                    avatar_url=""
                )
            )
            return resp
        finally:
            db.close()