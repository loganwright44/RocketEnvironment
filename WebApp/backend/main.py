#$ fastapi dev ./WebApp/backend/main.py

from fastapi import FastAPI

server = FastAPI()


@server.get("/")
async def root():
  return {
    "message": "API Online"
  }

