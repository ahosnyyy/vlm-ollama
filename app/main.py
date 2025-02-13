from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.clothing_info import router as image_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="API for analyzing images using VLM model",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Include routers
app.include_router(
    image_router,
    prefix=f"/api/{settings.api_version}",
    tags=["image-analysis"]
)

@app.get("/", tags=["status"])
async def read_root():
    """
    Root endpoint returning API information and status
    """
    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "analyze": f"/api/{settings.api_version}/analyze"
        }
    }