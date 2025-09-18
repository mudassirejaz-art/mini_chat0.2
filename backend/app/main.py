from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes,  chat_routes ,  image_routes
from app.middleware.rate_limit import RateLimiter
import logging
from sqlalchemy.orm import Session
from app.database import get_db

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Rate limiter
app.add_middleware(RateLimiter, max_requests=5, window_seconds=60)

# CORS
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ya ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(image_routes.router, prefix="/image", tags=["image"])  # 👈 new route

