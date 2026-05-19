from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import health, auth, projects, columns, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code here runs on startup
    print(f"{settings.APP_NAME} starting up...")
    yield
    # Code here runs on shutdown
    print(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Multi-tenant project management platform",
    lifespan=lifespan,
)

# CORS — allows the React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(columns.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}

