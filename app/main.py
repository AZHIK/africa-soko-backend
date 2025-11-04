# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    yield


app = FastAPI(title="AfricaSoko API", lifespan=lifespan)
