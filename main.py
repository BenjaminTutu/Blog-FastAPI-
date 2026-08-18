from fastapi import FastAPI
from database import Base, engine
from models import User, Post, Comment, Like

app = FastAPI()

print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)




