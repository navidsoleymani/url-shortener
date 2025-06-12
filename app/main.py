import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.api.routes import router
from app.db.admin import URLAdmin, URLVisitAdmin
from app.db.session import engine
from app.middleware.logging import add_logging_middleware

from .conf.application_lifespan import lifespan
from .conf.logging import configure_logging

# --- Logging Setup ---
configure_logging()

# --- App Initialization ---
app = FastAPI(
    title="URL Shortener",
    description="A modern, async URL shortening service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_logging_middleware(app)

# --- Routes ---
app.include_router(router)

# --- Admin Interface ---
admin = Admin(
    app,
    engine,
    title="Admin Dashboard",
    base_url="/admin",
    templates_dir="templates/admin"
)
admin.add_view(URLAdmin)
admin.add_view(URLVisitAdmin)
