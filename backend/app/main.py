"""
Main FastAPI Application

Zero-coupling API with plugin-based providers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logger import setup_logging, console
from app.routers import content, factory
from rich.panel import Panel

# Initialize
settings = get_settings()
setup_logging(level=settings.logging.level, colorize=settings.logging.colorize)

# Create FastAPI app
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="Modular YouTube Shorts Factory with swappable AI providers"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(factory.router, prefix="/api/factory", tags=["factory"])


@app.on_event("startup")
async def startup():
    """Show welcome message on startup."""
    console.print(Panel.fit(
        f"[bold cyan]{settings.app.name}[/bold cyan]\n"
        f"[dim]Version {settings.app.version}[/dim]\n\n"
        "[green]✓ API Server Ready[/green]\n"
        f"Docs: http://localhost:8000/docs",
        border_style="cyan"
    ))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app.name,
        "version": settings.app.version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}
