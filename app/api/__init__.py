"""API Router configuration"""
from fastapi import APIRouter

from app.api.endpoints import vacancies, companies, parser

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    vacancies.router,
    prefix="/vacancies",
    tags=["vacancies"]
)

api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["companies"]
)

api_router.include_router(
    parser.router,
    prefix="/parser",
    tags=["parser"]
)
