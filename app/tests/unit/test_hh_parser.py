import pytest
from unittest.mock import Mock, patch
from app.services.hh_parser import HHParser


class TestHHParser:
    """Юнит-тесты для HHParser"""

    @pytest.fixture
    def parser(self):
        """Создает экземпляр парсера для тестов"""
        return HHParser()

    def test_init(self, parser):
        """Тест инициализации парсера"""
        assert parser.base_url == "https://api.hh.ru/vacancies"
        assert parser.search_params is not None
        assert "Verilog" in parser.search_params["text"]

    @patch('app.services.hh_parser.requests.get')
    def test_search_vacancies_success(self, mock_get, parser):
        """Тест успешного поиска вакансий"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "12345678",
                    "name": "FPGA Developer",
                    "employer": {"name": "TechCorp"},
                    "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
                    "area": {"name": "Москва"},
                    "published_at": "2024-01-15T10:00:00",
                    "alternate_url": "https://hh.ru/vacancy/12345678",
                    "snippet": {
                        "requirement": "Опыт с Verilog",
                        "responsibility": "Разработка FPGA"
                    },
                    "experience": {"id": "between3And6"}
                }
            ],
            "found": 1,
            "pages": 1,
            "page": 0
        }
        mock_get.return_value = mock_response

        # Execute
        result = parser.search_vacancies()

        # Assert
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "FPGA Developer"
        mock_get.assert_called_once()

    @patch('app.services.hh_parser.requests.get')
    def test_search_vacancies_error(self, mock_get, parser):
        """Тест обработки ошибки при поиске"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = parser.search_vacancies()

        assert result is None

    def test_parse_vacancy_data(self, parser):
        """Тест парсинга данных вакансии"""
        vacancy = {
            "id": "12345678",
            "name": "FPGA Developer",
            "employer": {"name": "TechCorp"},
            "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
            "area": {"name": "Москва"},
            "published_at": "2024-01-15T10:00:00",
            "alternate_url": "https://hh.ru/vacancy/12345678",
            "snippet": {
                "requirement": "Опыт с Verilog",
                "responsibility": "Разработка FPGA"
            },
            "experience": {"id": "between3And6"}
        }

        parsed = parser.parse_vacancy_data(vacancy)

        assert parsed["hh_id"] == "12345678"
        assert parsed["name"] == "FPGA Developer"
        assert parsed["employer_name"] == "TechCorp"
        assert parsed["salary_from"] == 150000
        assert parsed["salary_to"] == 250000
        assert parsed["area_name"] == "Москва"

    def test_parse_vacancy_data_no_salary(self, parser):
        """Тест парсинга вакансии без зарплаты"""
        vacancy = {
            "id": "12345678",
            "name": "FPGA Developer",
            "employer": {"name": "TechCorp"},
            "salary": None,
            "area": {"name": "Москва"},
            "published_at": "2024-01-15T10:00:00",
            "alternate_url": "https://hh.ru/vacancy/12345678",
            "snippet": {
                "requirement": "Опыт",
                "responsibility": "Работа"
            },
            "experience": {"id": "noExperience"}
        }

        parsed = parser.parse_vacancy_data(vacancy)

        assert parsed["salary_from"] is None
        assert parsed["salary_to"] is None
        assert parsed["salary_currency"] is None

    @patch('app.services.hh_parser.requests.get')
    def test_get_employer_info_success(self, mock_get, parser):
        """Тест получения информации о работодателе"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "87654321",
            "name": "TechCorp",
            "alternate_url": "https://hh.ru/employer/87654321",
            "open_vacancies": 15
        }
        mock_get.return_value = mock_response

        result = parser.get_employer_info("87654321")

        assert result is not None
        assert result["id"] == "87654321"
        assert result["name"] == "TechCorp"
        assert result["open_vacancies"] == 15

    def test_filter_by_keywords(self, parser):
        """Тест фильтрации по ключевым словам"""
        vacancies = [
            {
                "name": "FPGA Developer",
                "snippet": {"requirement": "Опыт с Verilog, SystemVerilog"}
            },
            {
                "name": "Python Developer",
                "snippet": {"requirement": "Django, FastAPI"}
            },
            {
                "name": "ASIC Engineer",
                "snippet": {"requirement": "VHDL, Cadence"}
            }
        ]

        filtered = parser.filter_by_keywords(vacancies, ["Verilog", "VHDL"])

        assert len(filtered) == 2
        assert any("FPGA" in v["name"] for v in filtered)
        assert any("ASIC" in v["name"] for v in filtered)
