"""
Vacancies API endpoints
Эндпоинты для работы с вакансиями
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    VacancyResponse,
    VacancyCreate,
    VacancyUpdate,
)
from app.services.db_service import VacancyService

router = APIRouter()

# ============================================================================
# VACANCY ENDPOINTS
# ============================================================================

@router.get("/", response_model=Dict[str, Any])
async def get_vacancies(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    hh_id: Optional[str] = Query(None, description="Filter by HH.ru vacancy ID"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    status: Optional[str] = Query(None, description="Filter by vacancy status"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get list of vacancies with pagination
    
    Parameters:
    - page: Page number (starts from 1)
    - limit: Items per page (max 100)
    - hh_id: Filter by HH.ru vacancy ID
    - company_id: Filter by company ID
    - status: Filter by vacancy status
    
    Returns:
    - items: List of vacancies
    - total: Total count of vacancies
    - page: Current page
    - limit: Items per page
    - pages: Total number of pages
    """
    vacancy_service = VacancyService()
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get vacancies
    vacancies = vacancy_service.get_all(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        company_id=company_id
    )
    
    # Get total count
    total = vacancy_service.count(db, status=status, company_id=company_id)
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": vacancies,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages
    }


@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db)
) -> VacancyResponse:
    """
    Get specific vacancy by ID
    
    Parameters:
    - vacancy_id: Internal database ID of the vacancy
    """
    vacancy_service = VacancyService()
    vacancy = vacancy_service.get(db, vacancy_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found"
        )
    
    return vacancy


@router.get("/hh/{hh_id}", response_model=VacancyResponse)
async def get_vacancy_by_hh_id(
    hh_id: str,
    db: Session = Depends(get_db)
) -> VacancyResponse:
    """
    Get specific vacancy by HH.ru ID
    
    Parameters:
    - hh_id: HH.ru vacancy ID
    """
    vacancy_service = VacancyService()
    vacancy = vacancy_service.get_by_hh_id(db, hh_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with HH.ru ID {hh_id} not found"
        )
    
    return vacancy


@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy: VacancyCreate,
    db: Session = Depends(get_db)
) -> VacancyResponse:
    """
    Create a new vacancy
    
    Parameters:
    - vacancy: Vacancy data
    """
    vacancy_service = VacancyService()
    
    # Проверяем, не существует ли уже вакансия с таким hh_id
    existing = vacancy_service.get_by_hh_id(db, vacancy.hh_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vacancy with HH.ru ID {vacancy.hh_id} already exists"
        )
    
    try:
        return vacancy_service.create(db, vacancy)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vacancy: {str(e)}"
        )


@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    vacancy_update: VacancyUpdate,
    db: Session = Depends(get_db)
) -> VacancyResponse:
    """
    Update an existing vacancy
    
    Parameters:
    - vacancy_id: Internal database ID of the vacancy
    - vacancy_update: Updated vacancy data
    """
    vacancy_service = VacancyService()
    vacancy = vacancy_service.update(db, vacancy_id, vacancy_update)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found"
        )
    
    return vacancy


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a vacancy
    
    Parameters:
    - vacancy_id: Internal database ID of the vacancy
    """
    vacancy_service = VacancyService()
    success = vacancy_service.delete(db, vacancy_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found"
        )
    
    return None


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@router.get("/stats/summary")
async def get_vacancies_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics about vacancies
    """
    vacancy_service = VacancyService()
    
    total = vacancy_service.count(db)
    active = vacancy_service.count(db, status="active")
    
    return {
        "total_vacancies": total,
        "active_vacancies": active,
        "archived_vacancies": total - active
    }
