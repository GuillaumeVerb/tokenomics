from fastapi import FastAPI
from .middleware import setup_middlewares
from .api_docs import configure_openapi_docs

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
    return {"status": "healthy"} 