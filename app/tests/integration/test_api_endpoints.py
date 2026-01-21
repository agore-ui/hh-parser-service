import pytest
from fastapi import status


class TestVacanciesAPI:
    def test_get_vacancies_empty(self, client):
        response = client.get("/api/vacancies/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_vacancy(self, client, sample_vacancy_data):
        response = client.post("/api/vacancies/", json=sample_vacancy_data)
        assert response.status_code == status.HTTP_201_CREATED


class TestCompaniesAPI:
    def test_get_companies_empty(self, client):
        response = client.get("/api/companies/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_company(self, client, sample_company_data):
        response = client.post("/api/companies/", json=sample_company_data)
        assert response.status_code == status.HTTP_201_CREATED
