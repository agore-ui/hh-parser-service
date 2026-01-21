import pytest
from datetime import datetime
from app.services.db_service import DBService
from app.models import Vacancy, Company


class TestDBService:
    """Юнит-тесты для DBService"""

    @pytest.fixture
    def db_service(self, db_session):
        """Создает экземпляр DB service для тестов"""
        return DBService(db_session)

    def test_save_vacancy(self, db_service, db_session, sample_vacancy_data):
        """Тест сохранения вакансии"""
        db_service.save_vacancy(sample_vacancy_data)
        
        # Проверяем, что вакансия сохранена
        vacancy = db_session.query(Vacancy).filter_by(
            hh_id=sample_vacancy_data["hh_id"]
        ).first()
        
        assert vacancy is not None
        assert vacancy.name == sample_vacancy_data["name"]
        assert vacancy.employer_name == sample_vacancy_data["employer_name"]
        assert vacancy.salary_from == sample_vacancy_data["salary_from"]

    def test_save_vacancy_duplicate(self, db_service, db_session, sample_vacancy_data):
        """Тест обработки дубликата"""
        # Сохраняем вакансию дважды
        db_service.save_vacancy(sample_vacancy_data)
        db_service.save_vacancy(sample_vacancy_data)
        
        # Проверяем, что сохранена только одна запись
        count = db_session.query(Vacancy).filter_by(
            hh_id=sample_vacancy_data["hh_id"]
        ).count()
        
        assert count == 1

    def test_get_vacancy_by_hh_id(self, db_service, db_session, sample_vacancy_data):
        """Тест получения вакансии по ID"""
        db_service.save_vacancy(sample_vacancy_data)
        
        vacancy = db_service.get_vacancy_by_hh_id(sample_vacancy_data["hh_id"])
        
        assert vacancy is not None
        assert vacancy.name == sample_vacancy_data["name"]

    def test_get_vacancy_not_found(self, db_service):
        """Тест получения несуществующей вакансии"""
        vacancy = db_service.get_vacancy_by_hh_id("nonexistent")
        assert vacancy is None

    def test_get_all_vacancies(self, db_service, sample_vacancy_data):
        """Тест получения всех вакансий"""
        # Сохраняем несколько вакансий
        vacancy1 = sample_vacancy_data.copy()
        vacancy2 = sample_vacancy_data.copy()
        vacancy2["hh_id"] = "87654321"
        vacancy2["name"] = "ASIC Engineer"
        
        db_service.save_vacancy(vacancy1)
        db_service.save_vacancy(vacancy2)
        
        vacancies = db_service.get_all_vacancies()
        
        assert len(vacancies) == 2

    def test_get_vacancies_with_filters(self, db_service, sample_vacancy_data):
        """Тест фильтрации вакансий"""
        vacancy1 = sample_vacancy_data.copy()
        vacancy2 = sample_vacancy_data.copy()
        vacancy2["hh_id"] = "87654321"
        vacancy2["name"] = "Python Developer"
        
        db_service.save_vacancy(vacancy1)
        db_service.save_vacancy(vacancy2)
        
        # Фильтр по имени
        vacancies = db_service.get_vacancies_with_filters(name="FPGA")
        
        assert len(vacancies) == 1
        assert vacancies[0].name == "FPGA Developer"

    def test_save_company(self, db_service, db_session, sample_company_data):
        """Тест сохранения компании"""
        db_service.save_company(sample_company_data)
        
        company = db_session.query(Company).filter_by(
            hh_id=sample_company_data["hh_id"]
        ).first()
        
        assert company is not None
        assert company.name == sample_company_data["name"]
        assert company.vacancies_count == sample_company_data["vacancies_count"]

    def test_get_company_by_hh_id(self, db_service, sample_company_data):
        """Тест получения компании по ID"""
        db_service.save_company(sample_company_data)
        
        company = db_service.get_company_by_hh_id(sample_company_data["hh_id"])
        
        assert company is not None
        assert company.name == sample_company_data["name"]

    def test_get_all_companies(self, db_service, sample_company_data):
        """Тест получения всех компаний"""
        company1 = sample_company_data.copy()
        company2 = sample_company_data.copy()
        company2["hh_id"] = "11111111"
        company2["name"] = "SiliconCorp"
        
        db_service.save_company(company1)
        db_service.save_company(company2)
        
        companies = db_service.get_all_companies()
        
        assert len(companies) == 2

    def test_delete_vacancy(self, db_service, db_session, sample_vacancy_data):
        """Тест удаления вакансии"""
        db_service.save_vacancy(sample_vacancy_data)
        
        db_service.delete_vacancy(sample_vacancy_data["hh_id"])
        
        vacancy = db_session.query(Vacancy).filter_by(
            hh_id=sample_vacancy_data["hh_id"]
        ).first()
        
        assert vacancy is None

    def test_update_vacancy(self, db_service, db_session, sample_vacancy_data):
        """Тест обновления вакансии"""
        db_service.save_vacancy(sample_vacancy_data)
        
        # Обновляем данные
        updated_data = sample_vacancy_data.copy()
        updated_data["salary_from"] = 200000
        updated_data["salary_to"] = 300000
        
        db_service.update_vacancy(updated_data["hh_id"], updated_data)
        
        vacancy = db_session.query(Vacancy).filter_by(
            hh_id=sample_vacancy_data["hh_id"]
        ).first()
        
        assert vacancy.salary_from == 200000
        assert vacancy.salary_to == 300000
