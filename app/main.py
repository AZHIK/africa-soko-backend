from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.routers import auth


origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="AfricaSoko API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
