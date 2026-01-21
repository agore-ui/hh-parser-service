"""
SQLAlchemy модели для HH Parser Service
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Company(Base):
    """Модель компании-работодателя"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    hh_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    url = Column(String(500))
    description = Column(Text)
    site_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vacancies = relationship("Vacancy", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"


class Vacancy(Base):
    """Модель вакансии"""
    __tablename__ = 'vacancies'
    
    id = Column(Integer, primary_key=True, index=True)
    hh_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'))
    
    # Описание и требования
    description = Column(Text)
    key_skills = Column(JSON)  # ["Python", "FastAPI", ...]
    experience = Column(String(100))  # "От 1 до 3 лет"
    employment = Column(String(50))   # "Полная занятость"
    schedule = Column(String(50))     # "Полный день"
    
    # Зарплата
    salary_from = Column(Integer)
    salary_to = Column(Integer)
    salary_currency = Column(String(10))  # "RUR", "USD"
    salary_gross = Column(Boolean)        # До/после вычета налогов
    
    # Локация
    region = Column(String(100), index=True)
    city = Column(String(100))
    address = Column(Text)
    
    # Метаданные
    url = Column(String(500))
    status = Column(String(20), default='active', index=True)  # active, closed, archived
    published_at = Column(DateTime, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_checked_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="vacancies")
    versions = relationship("VacancyVersion", back_populates="vacancy", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_vacancy_company_status', 'company_id', 'status'),
        Index('ix_vacancy_published', 'published_at', 'status'),
    )
    
    def __repr__(self):
        return f"<Vacancy(id={self.id}, title='{self.title}', status='{self.status}')>"


class VacancyVersion(Base):
    """История изменений вакансии"""
    __tablename__ = 'vacancy_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey('vacancies.id', ondelete='CASCADE'), nullable=False)
    
    # Снимок данных на момент изменения
    title = Column(String(500))
    description = Column(Text)
    key_skills = Column(JSON)
    salary_from = Column(Integer)
    salary_to = Column(Integer)
    status = Column(String(20))
    
    # Метаданные изменения
    change_type = Column(String(50))  # created, updated, closed
    changed_fields = Column(JSON)     # ["salary_from", "description"]
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    vacancy = relationship("Vacancy", back_populates="versions")
    
    __table_args__ = (
        Index('ix_version_vacancy_created', 'vacancy_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<VacancyVersion(id={self.id}, vacancy_id={self.vacancy_id}, type='{self.change_type}')>"


class SearchFilter(Base):
    """Фильтр поиска вакансий"""
    __tablename__ = 'search_filters'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    
    # Параметры фильтра
    keywords = Column(JSON)      # ["FPGA", "ASIC", "Verilog"]
    regions = Column(JSON)       # [1, 2] - ID регионов HH.ru
    companies_include = Column(JSON)  # Включить компании
    companies_exclude = Column(JSON)  # Исключить компании
    
    # Настройки
    enabled = Column(Boolean, default=True, index=True)
    schedule_interval = Column(Integer, default=3600)  # Секунды между запусками
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_run_at = Column(DateTime)
    
    # Relationships
    tasks = relationship("ParsingTask", back_populates="filter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SearchFilter(id={self.id}, name='{self.name}', enabled={self.enabled})>"


class ParsingTask(Base):
    """Задача парсинга"""
    __tablename__ = 'parsing_tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    filter_id = Column(Integer, ForeignKey('search_filters.id', ondelete='CASCADE'))
    
    # Статус задачи
    status = Column(String(20), default='pending', index=True)  # pending, running, completed, failed
    
    # Результаты
    vacancies_found = Column(Integer, default=0)
    vacancies_new = Column(Integer, default=0)
    vacancies_updated = Column(Integer, default=0)
    vacancies_closed = Column(Integer, default=0)
    
    # Ошибки
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    filter = relationship("SearchFilter", back_populates="tasks")
    logs = relationship("ParsingLog", back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_task_status_created', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ParsingTask(id={self.id}, status='{self.status}', found={self.vacancies_found})>"


class ParsingLog(Base):
    """Логи парсинга"""
    __tablename__ = 'parsing_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('parsing_tasks.id', ondelete='CASCADE'))
    
    level = Column(String(20), index=True)  # INFO, WARNING, ERROR
    message = Column(Text)
    details = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    task = relationship("ParsingTask", back_populates="logs")
    
    def __repr__(self):
        return f"<ParsingLog(id={self.id}, level='{self.level}')>"


class AnalyticsDaily(Base):
    """Ежедневная аналитика"""
    __tablename__ = 'analytics_daily'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Статистика
    total_vacancies = Column(Integer, default=0)
    active_vacancies = Column(Integer, default=0)
    new_vacancies = Column(Integer, default=0)
    closed_vacancies = Column(Integer, default=0)
    
    # Разбивка по регионам
    by_region = Column(JSON)
    
    # Зарплатная статистика
    avg_salary_from = Column(Integer)
    avg_salary_to = Column(Integer)
    median_salary = Column(Integer)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<AnalyticsDaily(date={self.date}, total={self.total_vacancies})>"
