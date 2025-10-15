"""
CareerCompassAI FastAPI Backend

Main entry point for the CareerCompassAI API server.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from rich.console import Console

from app.core.config import settings
from app.core.database import init_db
from app.routers import resume, jobs, insights, agent

console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    console.print("🚀 Starting CareerCompassAI backend...", style="bold green")
    await init_db()
    console.print("✅ Database initialized", style="bold green")

    yield

    # Shutdown
    console.print("🛑 Shutting down CareerCompassAI backend...", style="bold red")


# Create FastAPI app
app = FastAPI(
    title="CareerCompassAI API",
    description="Intelligent career path recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CareerCompassAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CareerCompassAI", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
