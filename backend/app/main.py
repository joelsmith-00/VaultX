"""VaultX - FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("vaultx")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VaultX API starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("VaultX API shutting down...")

app = FastAPI(
    title="VaultX API",
    description="Secure cloud storage and smart file-sharing platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Register routers
from app.routers.auth import router as auth_router
app.include_router(auth_router)
from app.routers.files import router as files_router
app.include_router(files_router)
from app.routers.folders import router as folders_router
app.include_router(folders_router)
from app.routers.shares import router as shares_router
app.include_router(shares_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","Accept"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Auth middleware (decodes access tokens and attaches payload to `request.state`)
from app.middleware.auth import AuthMiddleware
app.add_middleware(AuthMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f}ms)")
    return response

@app.get("/", tags=["Root"])
async def root():
    return {"name": "VaultX API", "version": "1.0.0", "docs": "/api/docs"}

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0", "environment": settings.ENVIRONMENT}

@app.get("/api/health/detailed", tags=["Health"])
async def health_detailed():
    import redis.asyncio as aioredis
    results = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "storage": "unknown",
    }
    
    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        results["redis"] = "healthy"
    except Exception as e:
        results["redis"] = f"unhealthy: {str(e)}"
    
    overall = "healthy" if all(
        v == "healthy" for v in results.values()
    ) else "degraded"
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200 if overall == "healthy" else 503,
        content={"status": overall, **results}
    )
