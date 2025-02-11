"""
Main application package.
"""

from fastapi import FastAPI

from .api_docs import configure_openapi_docs
from .core.services import (  # Import services to ensure they are initialized
    cg,
    mongo_db,
)
from .middleware import setup_middlewares


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI()

    # Configure middlewares
    setup_middlewares(app)

    # Configure OpenAPI documentation
    configure_openapi_docs(app)

    # Import and include routers
    from .routers import simulation

    app.include_router(simulation.router, prefix="/simulate", tags=["Simulation"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint that also verifies database connection."""
        try:
            # Verify MongoDB connection
            mongo_db.command("ping")
            # Verify CoinGecko API
            cg.ping()
            return {
                "status": "healthy",
                "services": {"mongodb": "connected", "coingecko": "connected"},
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    return app


app = create_app()
