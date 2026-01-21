from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "HH Parser Service API"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
