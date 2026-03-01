"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, onboarding, menu, feedback, nutrition, personas, pantry, grocery

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    # Import all models so they're registered with Base
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="AI-powered weekly meal planner with a Saturday-to-Saturday cycle",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
cors_origins = settings.cors_origins
if isinstance(cors_origins, str):
    import json
    try:
        cors_origins = json.loads(cors_origins)
    except json.JSONDecodeError:
        cors_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(menu.router)
app.include_router(personas.router)
app.include_router(feedback.router)
app.include_router(nutrition.router)
app.include_router(pantry.router)
app.include_router(grocery.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}
