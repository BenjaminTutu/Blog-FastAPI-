from models import *
from main import app



@app.get("/")
async def home():
    return {"message": "Hello World"}

