from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Setup static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Include API router
app.include_router(api_router, prefix="/api/v1")

# UI Routes
@app.get("/ui/")
async def ui_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ui/vacancies")
async def ui_vacancies(request: Request):
    return templates.TemplateResponse("vacancies.html", {"request": request})

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
