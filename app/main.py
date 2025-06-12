import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.api.routes import router
from app.db.admin import URLAdmin, URLVisitAdmin
from app.db.session import engine
from app.middleware.logging import add_logging_middleware

from app.conf.application_lifespan import lifespan
from app.conf.logging import configure_logging

# --- Logging Setup ---
# Initialize logging before the application starts
configure_logging()

# --- App Initialization ---
app = FastAPI(
    title="URL Shortener",
    description="""
        A lightweight, fast, and extensible API to shorten URLs and track usage statistics.

        ## Features

        - 🔗 Shorten long URLs
        - 📥 Redirect using short codes
        - 📊 View number of visits per short code
    """,
    version="1.0.0",
    contact={
        "name": "Hydra",
        "url": "https://hydra.nvd",
        "email": "navidsoleymani@ymail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",           # Swagger UI path
    redoc_url="/redoc",         # ReDoc documentation path
    openapi_url="/openapi.json",  # OpenAPI spec path
    lifespan=lifespan           # Lifespan context for startup/shutdown hooks
)

# --- Middleware ---
# Enable CORS for frontend integration or external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom request logging middleware
add_logging_middleware(app)

# --- Routes ---
# Include all API routes
app.include_router(router)

# --- Admin Interface ---
# SQLAdmin interface for managing URL and visit models
admin = Admin(
    app,
    engine,
    title="Admin Dashboard",
    base_url="/admin",
    templates_dir="templates/admin"
)
admin.add_view(URLAdmin)
admin.add_view(URLVisitAdmin)
