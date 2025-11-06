from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.routers import auth, vendor, store, product, review, product_image, category


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
app.include_router(vendor.router, prefix="/vendors", tags=["Vendors"])
app.include_router(store.router, prefix="/stores", tags=["Stores"])
app.include_router(product.router)
app.include_router(review.router)
app.include_router(product_image.router)
app.include_router(category.router)
