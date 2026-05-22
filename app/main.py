from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.routers import health, auth, projects, columns, tasks, workspace, teams, billing, comments, users, notifications, dashboard
from app.db.mongodb import connect_mongodb, close_mongodb
from app.services.digest_service import send_overdue_digests

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongodb()
    scheduler.add_job(send_overdue_digests, 'cron', hour=12, minute=30)
    scheduler.start()
    print(f"Flowspace starting up...")
    yield
    scheduler.shutdown()
    close_mongodb()
    print(f"Flowspace shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Multi-tenant project management platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(columns.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(workspace.router)
app.include_router(teams.router)
app.include_router(billing.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}