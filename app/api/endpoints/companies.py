"""Companies API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CompanyCreate, CompanyUpdate, Company
from app.services.db_service import CompanyService

router = APIRouter()


@router.get("/", response_model=List[Company])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    hh_id: Optional[str] = Query(None, description="Filter by HH.ru company ID"),
    db: Session = Depends(get_db)
) -> List[Company]:
    """
    Get list of companies with optional filters
    
    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    - hh_id: Filter by HH.ru company ID
    """
    company_service = CompanyService()
    return company_service.get_all(db, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=Company)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
) -> Company:
    """
    Get specific company by ID
    
    Parameters:
    - company_id: Internal database ID of the company
    """
    company_service = CompanyService()
    company = company_service.get(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return company


@router.get("/hh/{hh_id}", response_model=Company)
async def get_company_by_hh_id(
    hh_id: str,
    db: Session = Depends(get_db)
) -> Company:
    """
    Get specific company by HH.ru ID
    
    Parameters:
    - hh_id: HH.ru company ID
    """
    company_service = CompanyService()
    company = company_service.get_by_hh_id(db, hh_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with HH.ru ID {hh_id} not found"
        )
    return company


@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
) -> Company:
    """
    Create a new company
    
    Parameters:
    - company: Company data
    """
    company_service = CompanyService()
    return company_service.create(db, company)


@router.put("/{company_id}", response_model=Company)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db)
) -> Company:
    """
    Update an existing company
    
    Parameters:
    - company_id: Internal database ID of the company
    - company_update: Updated company data
    """
    company_service = CompanyService()
    company = company_service.update(db, company_id, company_update)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a company
    
    Parameters:
    - company_id: Internal database ID of the company
    """
    company_service = CompanyService()
    success = company_service.delete(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return None
