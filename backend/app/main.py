"""
necessitas.ai FastAPI Backend

Main entry point for the necessitas.ai API server.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from rich.console import Console

from core.config import settings
from routers import resume, jobs, insights, company, chat

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    console.print("🚀 Starting necessitas.ai backend...", style="bold green")
    console.print("✅ API server initialized", style="bold green")

    yield

    # Shutdown
    console.print("🛑 Shutting down necessitas.ai backend...", style="bold red")


# Create FastAPI app
app = FastAPI(
    title="necessitas.ai API",
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
app.include_router(company.router, prefix="/api/company", tags=["company"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "necessitas.ai API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "necessitas.ai", "version": "1.0.0"}


@app.get("/test")
async def test_endpoint():
    """Test endpoint for debugging."""
    return {"message": "Backend is working!", "timestamp": "2024-01-20"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
