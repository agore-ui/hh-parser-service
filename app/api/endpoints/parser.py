"""Parser API endpoints"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ParsingRange
from app.services.hh_parser import HHParser
from app.services.db_service import VacancyService, CompanyService

router = APIRouter()


@router.post("/parse/", status_code=status.HTTP_202_ACCEPTED)
async def parse_vacancies(
    keywords: List[str],
    regions: Optional[List[int]] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start parsing vacancies from HH.ru based on keywords and regions
    
    Parameters:
    - keywords: List of keywords to search for
    - regions: List of region IDs (optional)
    - background_tasks: FastAPI background tasks
    - db: Database session
    
    Returns:
    - Status message with parsing information
    """
    parser = HHParser()
    
    # Get initial stats
    try:
        stats = parser.parse_and_save(
            keywords=keywords,
            regions=regions,
            params={}
        )
        
        return {
            "status": "completed",
            "message": "Parsing completed successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing failed: {str(e)}"
        )


@router.get("/search/", response_model=List[Dict[str, Any]])
async def search_vacancies(
    keywords: List[str],
    regions: Optional[List[int]] = None,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search vacancies from HH.ru without saving to database
    
    Parameters:
    - keywords: List of keywords to search for
    - regions: List of region IDs (optional)
    - params: Additional search parameters (optional)
    
    Returns:
    - List of found vacancies
    """
    parser = HHParser()
    
    try:
        vacancies = parser.search_vacancies(
            keywords=keywords,
            regions=regions,
            params=params or {}
        )
        return vacancies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/vacancy/{vacancy_id}", response_model=Dict[str, Any])
async def get_vacancy_details(
    vacancy_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a specific vacancy from HH.ru
    
    Parameters:
    - vacancy_id: HH.ru vacancy ID
    
    Returns:
    - Detailed vacancy information
    """
    parser = HHParser()
    
    try:
        vacancy_details = parser.get_vacancy_details(vacancy_id)
        if not vacancy_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacancy {vacancy_id} not found"
            )
        return vacancy_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vacancy details: {str(e)}"
        )


@router.get("/company/{company_id}", response_model=Dict[str, Any])
async def get_company_info(
    company_id: str
) -> Dict[str, Any]:
    """
    Get company information from HH.ru
    
    Parameters:
    - company_id: HH.ru company ID
    
    Returns:
    - Company information
    """
    parser = HHParser()
    
    try:
        company_info = parser._parse_company({"id": company_id})
        if not company_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {company_id} not found"
            )
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company info: {str(e)}"
        )
