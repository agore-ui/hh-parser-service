"""Vacancies API endpoints"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    VacancyCreate,
    VacancyUpdate,
    Vacancy,
    SearchFilterCreate,
    SearchFilterUpdate,
    SearchFilter,
    AnalyticallyCreate,
    AnalyticallyUpdate,
    Analytically,
    ParsingRange
)
from app.services.db_service import VacancyService, SearchFilterService, AnalyticallyService

router = APIRouter()


# ============ Vacancy Endpoints ============

@router.get("/", response_model=List[Vacancy])
async def get_vacancies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    hh_id: Optional[str] = Query(None, description="Filter by HH.ru vacancy ID"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    status: Optional[str] = Query(None, description="Filter by vacancy status"),
    db: Session = Depends(get_db)
) -> List[Vacancy]:
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
    return vacancy_service.get_all(db, skip=skip, limit=limit)


@router.get("/{vacancy_id}", response_model=Vacancy)
async def get_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db)
) -> Vacancy:
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


@router.get("/hh/{hh_id}", response_model=Vacancy)
async def get_vacancy_by_hh_id(
    hh_id: str,
    db: Session = Depends(get_db)
) -> Vacancy:
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


@router.post("/", response_model=Vacancy, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy: VacancyCreate,
    db: Session = Depends(get_db)
) -> Vacancy:
    """
    Create a new vacancy
    
    Parameters:
    - vacancy: Vacancy data
    """
    vacancy_service = VacancyService()
    return vacancy_service.create(db, vacancy)


@router.put("/{vacancy_id}", response_model=Vacancy)
async def update_vacancy(
    vacancy_id: int,
    vacancy_update: VacancyUpdate,
    db: Session = Depends(get_db)
) -> Vacancy:
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


# ============ Search Filter Endpoints ============

@router.get("/filters/", response_model=List[SearchFilter])
async def get_search_filters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[SearchFilter]:
    """
    Get list of search filters
    """
    filter_service = SearchFilterService()
    return filter_service.get_all(db, skip=skip, limit=limit)


@router.get("/filters/{filter_id}", response_model=SearchFilter)
async def get_search_filter(
    filter_id: int,
    db: Session = Depends(get_db)
) -> SearchFilter:
    """
    Get specific search filter by ID
    """
    filter_service = SearchFilterService()
    search_filter = filter_service.get(db, filter_id)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search filter with id {filter_id} not found"
        )
    return search_filter


@router.post("/filters/", response_model=SearchFilter, status_code=status.HTTP_201_CREATED)
async def create_search_filter(
    search_filter: SearchFilterCreate,
    db: Session = Depends(get_db)
) -> SearchFilter:
    """
    Create a new search filter
    """
    filter_service = SearchFilterService()
    return filter_service.create(db, search_filter)


@router.put("/filters/{filter_id}", response_model=SearchFilter)
async def update_search_filter(
    filter_id: int,
    filter_update: SearchFilterUpdate,
    db: Session = Depends(get_db)
) -> SearchFilter:
    """
    Update an existing search filter
    """
    filter_service = SearchFilterService()
    search_filter = filter_service.update(db, filter_id, filter_update)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search filter with id {filter_id} not found"
        )
    return search_filter


@router.delete("/filters/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_filter(
    filter_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a search filter
    """
    filter_service = SearchFilterService()
    success = filter_service.delete(db, filter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search filter with id {filter_id} not found"
        )
    return None


# ============ Analytically Endpoints ============

@router.get("/analytics/", response_model=List[Analytically])
async def get_analytics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[Analytically]:
    """
    Get list of analytics records
    """
    analytics_service = AnalyticallyService()
    return analytics_service.get_all(db, skip=skip, limit=limit)


@router.get("/analytics/{analytics_id}", response_model=Analytically)
async def get_analytics_record(
    analytics_id: int,
    db: Session = Depends(get_db)
) -> Analytically:
    """
    Get specific analytics record by ID
    """
    analytics_service = AnalyticallyService()
    analytics = analytics_service.get(db, analytics_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics record with id {analytics_id} not found"
        )
    return analytics


@router.post("/analytics/", response_model=Analytically, status_code=status.HTTP_201_CREATED)
async def create_analytics(
    analytics: AnalyticallyCreate,
    db: Session = Depends(get_db)
) -> Analytically:
    """
    Create a new analytics record
    """
    analytics_service = AnalyticallyService()
    return analytics_service.create(db, analytics)


@router.put("/analytics/{analytics_id}", response_model=Analytically)
async def update_analytics(
    analytics_id: int,
    analytics_update: AnalyticallyUpdate,
    db: Session = Depends(get_db)
) -> Analytically:
    """
    Update an existing analytics record
    """
    analytics_service = AnalyticallyService()
    analytics = analytics_service.update(db, analytics_id, analytics_update)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics record with id {analytics_id} not found"
        )
    return analytics


@router.delete("/analytics/{analytics_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analytics(
    analytics_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an analytics record
    """
    analytics_service = AnalyticallyService()
    success = analytics_service.delete(db, analytics_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics record with id {analytics_id} not found"
        )
    return None
