from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .api.endpoints import prediction, simulation
from .core.config import settings
from .middleware import setup_middlewares
from .routers import simulation as simulation_router

app = FastAPI(
    title="Tokenomics API",
    description="API for tokenomics simulation and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middlewares
setup_middlewares(app)

# Include routers
app.include_router(simulation_router.router, prefix="/simulate", tags=["simulation"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Tokenomics API",
        version="1.0.0",
        description="API for tokenomics simulation and analysis",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
