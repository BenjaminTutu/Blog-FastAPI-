from fastapi import FastAPI

import admin
import auth
import blog
from database import Base, engine
from models import User, Post, Comment, Like

app = FastAPI()

# print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)


@app.get("/")
async def home():
    return {"message": "Hello World"}



app.include_router(blog.router)
app.include_router(auth.router)
app.include_router(admin.router)



