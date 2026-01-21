import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# Тестовая база данных в памяти
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Создает чистую БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Предоставляет сессию БД для теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент FastAPI с переопределенной БД"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_vacancy_data():
    """Тестовые данные вакансии"""
    return {
        "hh_id": "12345678",
        "name": "FPGA Developer",
        "employer_name": "TechCorp",
        "salary_from": 150000,
        "salary_to": 250000,
        "salary_currency": "RUR",
        "area_name": "Москва",
        "published_at": "2024-01-15T10:00:00",
        "url": "https://hh.ru/vacancy/12345678",
        "requirement": "Опыт с Verilog, SystemVerilog",
        "responsibility": "Разработка FPGA",
        "experience": "between3And6"
    }


@pytest.fixture
def sample_company_data():
    """Тестовые данные компании"""
    return {
        "hh_id": "87654321",
        "name": "TechCorp",
        "url": "https://hh.ru/employer/87654321",
        "vacancies_count": 15
    }
