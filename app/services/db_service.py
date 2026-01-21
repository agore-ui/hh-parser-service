"""Database Service - CRUD operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from app.models import Company, Vacancy, VacancyVersion, SearchFilter, ParsingTask, ParsingLog, AnalyticsDaily
from app.schemas import CompanyCreate, CompanyUpdate, VacancyCreate, VacancyUpdate, SearchFilterCreate, SearchFilterUpdate

class CompanyService:
    @staticmethod
    def get(db: Session, company_id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == company_id).first()
    
    @staticmethod
    def get_by_hh_id(db: Session, hh_id: str) -> Optional[Company]:
        return db.query(Company).filter(Company.hh_id == hh_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, company: CompanyCreate) -> Company:
        db_company = Company(**company.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    
    @staticmethod
    def update(db: Session, company_id: int, company_update: CompanyUpdate) -> Optional[Company]:
        db_company = CompanyService.get(db, company_id)
        if not db_company:
            return None
        update_data = company_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)
        db_company.updated_at = datetime.now()
        db.commit()
        db.refresh(db_company)
        return db_company

class VacancyService:
    @staticmethod
    def get(db: Session, vacancy_id: int) -> Optional[Vacancy]:
        return db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    
    @staticmethod
    def get_by_hh_id(db: Session, hh_id: str) -> Optional[Vacancy]:
        return db.query(Vacancy).filter(Vacancy.hh_id == hh_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, region: Optional[str] = None, company_id: Optional[int] = None) -> List[Vacancy]:
        query = db.query(Vacancy)
        if status:
            query = query.filter(Vacancy.status == status)
        if region:
            query = query.filter(Vacancy.region == region)
        if company_id:
            query = query.filter(Vacancy.company_id == company_id)
        return query.order_by(desc(Vacancy.published_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def search(db: Session, keywords: Optional[List[str]] = None, min_salary: Optional[int] = None, max_salary: Optional[int] = None, experience: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Vacancy]:
        query = db.query(Vacancy)
        if keywords:
            keyword_filter = or_(*[Vacancy.title.ilike(f"%{kw}%") for kw in keywords], *[Vacancy.description.ilike(f"%{kw}%") for kw in keywords])
            query = query.filter(keyword_filter)
        if min_salary:
            query = query.filter(Vacancy.salary_from >= min_salary)
        if max_salary:
            query = query.filter(Vacancy.salary_to <= max_salary)
        if experience:
            query = query.filter(Vacancy.experience == experience)
        return query.order_by(desc(Vacancy.published_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def count(db: Session, status: Optional[str] = None) -> int:
        query = db.query(func.count(Vacancy.id))
        if status:
            query = query.filter(Vacancy.status == status)
        return query.scalar()
    
    @staticmethod
    def get_history(db: Session, vacancy_id: int) -> List[VacancyVersion]:
        return db.query(VacancyVersion).filter(VacancyVersion.vacancy_id == vacancy_id).order_by(desc(VacancyVersion.created_at)).all()

class SearchFilterService:
    @staticmethod
    def get(db: Session, filter_id: int) -> Optional[SearchFilter]:
        return db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    
    @staticmethod
    def get_all(db: Session, enabled_only: bool = False) -> List[SearchFilter]:
        query = db.query(SearchFilter)
        if enabled_only:
            query = query.filter(SearchFilter.enabled == True)
        return query.all()
    
    @staticmethod
    def create(db: Session, filter_data: SearchFilterCreate) -> SearchFilter:
        db_filter = SearchFilter(**filter_data.dict())
        db.add(db_filter)
        db.commit()
        db.refresh(db_filter)
        return db_filter
    
    @staticmethod
    def update(db: Session, filter_id: int, filter_update: SearchFilterUpdate) -> Optional[SearchFilter]:
        db_filter = SearchFilterService.get(db, filter_id)
        if not db_filter:
            return None
        update_data = filter_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_filter, field, value)
        db_filter.updated_at = datetime.now()
        db.commit()
        db.refresh(db_filter)
        return db_filter
    
    @staticmethod
    def delete(db: Session, filter_id: int) -> bool:
        db_filter = SearchFilterService.get(db, filter_id)
        if not db_filter:
            return False
        db.delete(db_filter)
        db.commit()
        return True
    
    @staticmethod
    def update_last_run(db: Session, filter_id: int):
        db_filter = SearchFilterService.get(db, filter_id)
        if db_filter:
            db_filter.last_run_at = datetime.now()
            db.commit()

class ParsingTaskService:
    @staticmethod
    def get(db: Session, task_id: int) -> Optional[ParsingTask]:
        return db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
    
    @staticmethod
    def get_all(db: Session, status: Optional[str] = None, limit: int = 50) -> List[ParsingTask]:
        query = db.query(ParsingTask)
        if status:
            query = query.filter(ParsingTask.status == status)
        return query.order_by(desc(ParsingTask.created_at)).limit(limit).all()
    
    @staticmethod
    def create(db: Session, filter_id: Optional[int] = None) -> ParsingTask:
        task = ParsingTask(filter_id=filter_id, status="pending")
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def update_status(db: Session, task_id: int, status: str, **kwargs) -> Optional[ParsingTask]:
        task = ParsingTaskService.get(db, task_id)
        if not task:
            return None
        task.status = status
        if status == "running":
            task.started_at = datetime.now()
        elif status in ["completed", "failed"]:
            task.completed_at = datetime.now()
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def add_log(db: Session, task_id: int, level: str, message: str, details: Optional[Dict] = None):
        log = ParsingLog(task_id=task_id, level=level, message=message, details=details)
        db.add(log)
        db.commit()
    
    @staticmethod
    def get_logs(db: Session, task_id: int) -> List[ParsingLog]:
        return db.query(ParsingLog).filter(ParsingLog.task_id == task_id).order_by(ParsingLog.created_at).all()

class AnalyticsService:
    @staticmethod
    def get_daily_stats(db: Session, date: datetime) -> Optional[AnalyticsDaily]:
        return db.query(AnalyticsDaily).filter(func.date(AnalyticsDaily.date) == date.date()).first()
    
    @staticmethod
    def get_stats_range(db: Session, start_date: datetime, end_date: datetime) -> List[AnalyticsDaily]:
        return db.query(AnalyticsDaily).filter(and_(AnalyticsDaily.date >= start_date, AnalyticsDaily.date <= end_date)).order_by(AnalyticsDaily.date).all()
    
    @staticmethod
    def calculate_overall_stats(db: Session) -> Dict[str, Any]:
        total_vacancies = db.query(func.count(Vacancy.id)).scalar()
        active_vacancies = db.query(func.count(Vacancy.id)).filter(Vacancy.status == "active").scalar()
        total_companies = db.query(func.count(Company.id)).scalar()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        vacancies_today = db.query(func.count(Vacancy.id)).filter(Vacancy.created_at >= today_start).scalar()
        vacancies_week = db.query(func.count(Vacancy.id)).filter(Vacancy.created_at >= week_ago).scalar()
        vacancies_month = db.query(func.count(Vacancy.id)).filter(Vacancy.created_at >= month_ago).scalar()
        top_regions = db.query(Vacancy.region, func.count(Vacancy.id).label("count")).filter(Vacancy.region.isnot(None)).group_by(Vacancy.region).order_by(desc("count")).limit(10).all()
        salary_stats = db.query(func.avg(Vacancy.salary_from).label("avg_from"), func.avg(Vacancy.salary_to).label("avg_to"), func.min(Vacancy.salary_from).label("min_from"), func.max(Vacancy.salary_to).label("max_to")).filter(Vacancy.salary_from.isnot(None)).first()
        return {"total_vacancies": total_vacancies, "active_vacancies": active_vacancies, "total_companies": total_companies, "vacancies_today": vacancies_today, "vacancies_week": vacancies_week, "vacancies_month": vacancies_month, "top_keywords": [], "top_regions": [{"region": r[0], "count": r[1]} for r in top_regions], "salary_stats": {"avg_from": float(salary_stats.avg_from) if salary_stats.avg_from else None, "avg_to": float(salary_stats.avg_to) if salary_stats.avg_to else None, "min_from": salary_stats.min_from, "max_to": salary_stats.max_to} if salary_stats else {}}

# КОНЕЦ ФАЙЛА db_service.py
