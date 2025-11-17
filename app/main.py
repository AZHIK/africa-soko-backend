from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.init_db import init_db
from app.routers import (
    auth,
    vendor,
    store,
    product,
    review,
    product_image,
    category,
    user,
    location,  # Added location router
    uploads,
    stories,
    chats,
    orders,
)


origins = ["https://repeated-coated-boolean-honest.trycloudflare.com", "197.186.8.40"]


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

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routers
app.include_router(auth.router, prefix="/authenticate", tags=["auth"])
app.include_router(vendor.router, prefix="/vendors", tags=["Vendors"])
app.include_router(store.router, prefix="/stores", tags=["Stores"])
app.include_router(product.router)
app.include_router(review.router)
app.include_router(product_image.router)
app.include_router(category.router)
app.include_router(user.router)
app.include_router(location.router, tags=["Locations"])
app.include_router(uploads.router)
app.include_router(stories.router)
app.include_router(chats.router)
app.include_router(orders.router)


@app.websocket("/online_status")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for online status.
    Manually checks the Origin header to allow connections.
    """
    origin = websocket.headers.get("origin")

    if origin not in origins:
        await websocket.close(code=1008)  # Policy Violation
        return

    await websocket.accept()
    try:
        while True:
            # This endpoint will keep the connection alive.
            # You can add logic here to receive messages or broadcast status updates.
            # For now, it waits for a message before closing.
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"Client {websocket.client.host} disconnected.")
