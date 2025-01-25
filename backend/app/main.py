from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import simulation

app = FastAPI(
    title="Tokenomics API",
    description="API for tokenomics simulations and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulation.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 