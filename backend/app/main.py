"""
FastAPI main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, close_db
from app.datasets import dataset_loader
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 ShootSafe AI Backend starting...")
    
    # Initialize database (non-blocking)
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization skipped: {e}")
        logger.warning("ℹ️ System will run without persistent storage")
    
    # Load datasets
    try:
        dataset_loader.load_all()
        logger.info("✅ Datasets loaded")
    except Exception as e:
        logger.warning(f"⚠️ Dataset loading skipped: {e}")
    
    logger.info("✅ Startup complete - API ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    try:
        await close_db()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.warning(f"⚠️ Database shutdown warning: {e}")
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="ShootSafe AI",
    description="Film production safety & budgeting system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== HEALTH CHECK ==============
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ShootSafe AI Backend",
        "version": "0.1.0"
    }


# ============== ROOT ==============
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ShootSafe AI",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============== INCLUDE ROUTERS ==============
# Import all v1 API routers
from app.api.v1 import projects, uploads, runs, results, whatif, reports

# Include routers with proper prefixes
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(uploads.router, prefix="/api/v1/projects", tags=["Uploads"])
app.include_router(runs.router, prefix="/api/v1/runs", tags=["Runs"])
app.include_router(results.router, prefix="/api/v1/results", tags=["Results"])
app.include_router(whatif.router, prefix="/api/v1/whatif", tags=["What-If"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
