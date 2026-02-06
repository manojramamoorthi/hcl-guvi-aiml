"""
FastAPI main application
SME Financial Health Assessment Platform
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import os
from contextlib import asynccontextmanager

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database.database import init_db

# Configure logging
logger.add(
    settings.LOG_FILE,
    rotation="1 day",
    retention="30 days",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def  lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SME Financial Platform...")
    logger.info(f"Initializing database...")
    init_db()
    logger.info("✓ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SME Financial Platform...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered financial health assessment platform for SMEs",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs"
    }

# Import and include routers
try:
    from routes import auth_routes, company_routes, upload_routes, analysis_routes
    
    app.include_router(auth_routes.router, prefix=settings.API_PREFIX, tags=["Authentication"])
    app.include_router(company_routes.router, prefix=settings.API_PREFIX, tags=["Company"])
    app.include_router(upload_routes.router, prefix=settings.API_PREFIX, tags=["Upload"])
    app.include_router(analysis_routes.router, prefix=settings.API_PREFIX, tags=["Analysis"])
    
    logger.info("✓ All routes registered successfully")
except ImportError as e:
    logger.warning(f"Some routes not available yet: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
