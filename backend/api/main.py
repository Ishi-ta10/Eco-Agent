"""
Main FastAPI application
Energy Dashboard API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import data, kpis, export, scheduler
from .services import scheduler_service

# Create FastAPI app
app = FastAPI(
    title="Energy Dashboard API",
    description="API for Energy Consumption Dashboard - Noida Campus",
    version="1.0.0"
)

# Configure CORS - Allow all localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8890",
        "http://127.0.0.1:8890",
        "http://localhost:8888",
        "http://127.0.0.1:8888",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router)
app.include_router(kpis.router)
app.include_router(export.router)
app.include_router(scheduler.router)


@app.on_event("startup")
async def startup_event():
    """Load persisted scheduler state on API startup."""
    scheduler_service.initialize_scheduler_from_config()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Energy Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "data": "/api/data",
            "kpis": "/api/kpis",
            "export": "/api/export",
            "scheduler": "/api/scheduler"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
