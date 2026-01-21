"""
Vacancies API endpoints
Эндпоинты для работы с вакансиями
"""
from typing import List, Optional
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

@router.get("/", response_model=List[VacancyResponse])
async def get_vacancies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    hh_id: Optional[str] = Query(None, description="Filter by HH.ru vacancy ID"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    status: Optional[str] = Query(None, description="Filter by vacancy status"),
    db: Session = Depends(get_db)
) -> List[VacancyResponse]:
    """
    Get list of vacancies with optional filters
    
    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    - hh_id: Filter by HH.ru vacancy ID
    - company_id: Filter by company ID
    - status: Filter by vacancy status
    """
    vacancy_service = VacancyService()
    return vacancy_service.get_all(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        company_id=company_id
    )


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
