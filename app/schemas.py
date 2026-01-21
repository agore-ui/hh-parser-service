"""
Pydantic схемы для валидации данных API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator


# ============================================================================
# COMPANY SCHEMAS
# ============================================================================

class CompanyBase(BaseModel):
    """Базовая схема компании"""
    hh_id: str = Field(..., description="ID компании на HH.ru")
    name: str = Field(..., max_length=500, description="Название компании")
    url: Optional[str] = Field(None, description="URL компании на HH.ru")
    description: Optional[str] = Field(None, description="Описание компании")
    site_url: Optional[str] = Field(None, description="Сайт компании")


class CompanyCreate(CompanyBase):
    """Схема создания компании"""
    pass


class CompanyUpdate(BaseModel):
    """Схема обновления компании"""
    name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    site_url: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Схема ответа с данными компании"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# VACANCY SCHEMAS
# ============================================================================

class VacancyBase(BaseModel):
    """Базовая схема вакансии"""
    hh_id: str = Field(..., description="ID вакансии на HH.ru")
    title: str = Field(..., max_length=500, description="Название вакансии")
    description: Optional[str] = Field(None, description="Описание вакансии")
    key_skills: Optional[List[str]] = Field(default_factory=list, description="Ключевые навыки")
    experience: Optional[str] = Field(None, description="Требуемый опыт")
    employment: Optional[str] = Field(None, description="Тип занятости")
    schedule: Optional[str] = Field(None, description="График работы")
    
    # Зарплата
    salary_from: Optional[int] = Field(None, ge=0, description="Зарплата от")
    salary_to: Optional[int] = Field(None, ge=0, description="Зарплата до")
    salary_currency: Optional[str] = Field(None, description="Валюта")
    salary_gross: Optional[bool] = Field(None, description="До вычета налогов")
    
    # Локация
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    address: Optional[str] = Field(None, description="Адрес")
    
    # Метаданные
    url: Optional[str] = Field(None, description="URL вакансии")
    status: str = Field(default="active", description="Статус вакансии")
    published_at: Optional[datetime] = Field(None, description="Дата публикации")


class VacancyCreate(VacancyBase):
    """Схема создания вакансии"""
    company_id: int = Field(..., description="ID компании")


class VacancyUpdate(BaseModel):
    """Схема обновления вакансии"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    key_skills: Optional[List[str]] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    status: Optional[str] = None


class VacancyResponse(VacancyBase):
    """Схема ответа с данными вакансии"""
    id: int
    company_id: int
    company: Optional[CompanyResponse] = None
    created_at: datetime
    updated_at: Optional[datetime]
    last_checked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VacancyListResponse(BaseModel):
    """Схема списка вакансий с пагинацией"""
    items: List[VacancyResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# SEARCH FILTER SCHEMAS
# ============================================================================

class SearchFilterBase(BaseModel):
    """Базовая схема фильтра поиска"""
    name: str = Field(..., max_length=200, description="Название фильтра")
    description: Optional[str] = Field(None, description="Описание фильтра")
    keywords: List[str] = Field(default_factory=list, description="Ключевые слова")
    regions: List[int] = Field(default_factory=list, description="ID регионов HH.ru")
    companies_include: Optional[List[str]] = Field(default_factory=list, description="Включить компании")
    companies_exclude: Optional[List[str]] = Field(default_factory=list, description="Исключить компании")
    enabled: bool = Field(default=True, description="Фильтр активен")
    schedule_interval: int = Field(default=3600, ge=60, description="Интервал запуска в секундах")


class SearchFilterCreate(SearchFilterBase):
    """Схема создания фильтра"""
    pass


class SearchFilterUpdate(BaseModel):
    """Схема обновления фильтра"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    regions: Optional[List[int]] = None
    companies_include: Optional[List[str]] = None
    companies_exclude: Optional[List[str]] = None
    enabled: Optional[bool] = None
    schedule_interval: Optional[int] = Field(None, ge=60)


class SearchFilterResponse(SearchFilterBase):
    """Схема ответа с данными фильтра"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_run_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# PARSING TASK SCHEMAS
# ============================================================================

class ParsingTaskResponse(BaseModel):
    """Схема ответа с данными задачи парсинга"""
    id: int
    filter_id: int
    status: str
    vacancies_found: int
    vacancies_new: int
    vacancies_updated: int
    vacancies_closed: int
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ParsingTaskCreate(BaseModel):
    """Схема запуска парсинга"""
    filter_id: Optional[int] = Field(None, description="ID фильтра (опционально)")
    keywords: Optional[List[str]] = Field(None, description="Ключевые слова")
    regions: Optional[List[int]] = Field(None, description="Регионы")


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class AnalyticsDailyResponse(BaseModel):
    """Схема ежедневной аналитики"""
    id: int
    date: datetime
    total_vacancies: int
    active_vacancies: int
    new_vacancies: int
    closed_vacancies: int
    by_region: Optional[Dict[str, int]]
    avg_salary_from: Optional[int]
    avg_salary_to: Optional[int]
    median_salary: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsStatsResponse(BaseModel):
    """Общая статистика"""
    total_vacancies: int
    active_vacancies: int
    total_companies: int
    vacancies_today: int
    vacancies_week: int
    vacancies_month: int
    top_keywords: List[Dict[str, Any]]
    top_regions: List[Dict[str, Any]]
    salary_stats: Dict[str, Any]


# ============================================================================
# GENERAL SCHEMAS
# ============================================================================

class HealthResponse(BaseModel):
    """Схема health check"""
    status: str
    service: str
    environment: str
    timestamp: datetime
    database: str
    redis: str


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Aliases для обратной совместимости
Vacancy = VacancyResponse
Company = CompanyResponse
SearchFilter = SearchFilterResponse
Analytically = AnalyticsDailyResponse
AnalyticallyCreate = AnalyticsDailyResponse
AnalyticallyUpdate = AnalyticsDailyResponse
ParsingRange = ParsingTaskCreate

# Aliases для обратной совместимости
Vacancy = VacancyResponse
Company = CompanyResponse
SearchFilter = SearchFilterResponse
Analytically = AnalyticsDailyResponse
AnalyticallyCreate = AnalyticsDailyResponse
AnalyticallyUpdate = AnalyticsDailyResponse
ParsingRange = ParsingTaskCreate
