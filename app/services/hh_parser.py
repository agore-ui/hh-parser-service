# HH.ru Parser Service - placeholder, will be implemented soon
"""
HH.ru Parser Service
"""
import asyncio
import aiohttp
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models import Company, Vacancy, VacancyVersion
from config import settings

logger = logging.getLogger(__name__)

class HHParserError(Exception):
    pass

class HHRateLimitError(HHParserError):
    pass

class HHParser:
    BASE_URL = "https://api.hh.ru"
    VACANCIES_PER_PAGE = 100
    MAX_PAGES = 20
    REQUEST_DELAY = 0.35
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 2.0
    
    EXPERIENCE_CODES = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }
    
    def __init__(self, db: Session, user_agent: Optional[str] = None):
        self.db = db
        self.user_agent = user_agent or f"{settings.APP_NAME}/1.0"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None, retry_count: int = 0) -> Dict[str, Any]:
        if not self.session:
            raise HHParserError("Session not initialized")
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 429:
                    if retry_count < self.RETRY_ATTEMPTS:
                        await asyncio.sleep(self.RETRY_DELAY * (retry_count + 1))
                        return await self._make_request(endpoint, params, retry_count + 1)
                    raise HHRateLimitError("Rate limit exceeded")
                
                if response.status != 200:
                    raise HHParserError(f"API returned {response.status}")
                
                return await response.json()
        except asyncio.TimeoutError:
            if retry_count < self.RETRY_ATTEMPTS:
                await asyncio.sleep(self.RETRY_DELAY)
                return await self._make_request(endpoint, params, retry_count + 1)
            raise HHParserError("Timeout")
        except aiohttp.ClientError as e:
            if retry_count < self.RETRY_ATTEMPTS:
                await asyncio.sleep(self.RETRY_DELAY)
                return await self._make_request(endpoint, params, retry_count + 1)
            raise HHParserError(f"Network error: {e}")
    
    async def search_vacancies(self, keywords: List[str], regions: Optional[List[int]] = None, **kwargs) -> List[Dict]:
        all_vacancies = []
        for keyword in keywords:
            logger.info(f"Поиск: '{keyword}'")
            params = {"text": keyword, "per_page": self.VACANCIES_PER_PAGE, "page": 0, "period": 30}
            if regions:
                params["area"] = regions[0] if len(regions) == 1 else regions
            
            page = 0
            while page < self.MAX_PAGES:
                params["page"] = page
                try:
                    data = await self._make_request("/vacancies", params)
                    vacancies = data.get("items", [])
                    if not vacancies:
                        break
                    all_vacancies.extend(vacancies)
                    if page >= data.get("pages", 1) - 1:
                        break
                    page += 1
                    await asyncio.sleep(self.REQUEST_DELAY)
                except HHParserError as e:
                    logger.error(f"Ошибка: {e}")
                    break
        
        unique = {v["id"]: v for v in all_vacancies}.values()
        return list(unique)
    
    async def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict]:
        try:
            details = await self._make_request(f"/vacancies/{vacancy_id}")
            await asyncio.sleep(self.REQUEST_DELAY)
            return details
        except HHParserError:
            return None

    def _parse_company(self, company_data: Optional[Dict]) -> Optional[Company]:
        if not company_data or not company_data.get("id"):
            return None
        
        company = self.db.query(Company).filter(Company.hh_id == str(company_data["id"])).first()
        if company:
            company.name = company_data.get("name", company.name)
            company.updated_at = datetime.now()
        else:
            company = Company(
                hh_id=str(company_data["id"]),
                name=company_data.get("name", "Неизвестно"),
                url=company_data.get("alternate_url")
            )
            self.db.add(company)
        self.db.flush()
        return company
    
    def _parse_vacancy(self, vac_data: Dict, company: Company) -> Tuple[Vacancy, bool]:
        v_id = vac_data.get("id")
        existing = self.db.query(Vacancy).filter(Vacancy.hh_id == str(v_id)).first()
        
        salary = vac_data.get("salary")
        skills = [s.get("name") for s in vac_data.get("key_skills", []) if s.get("name")]
        pub_at = None
        if "published_at" in vac_data:
            try:
                pub_at = datetime.fromisoformat(vac_data["published_at"].replace("Z", "+00:00"))
            except:
                pass
        
        if not existing:
            vacancy = Vacancy(
                hh_id=str(v_id),
                company_id=company.id,
                title=vac_data.get("name", "Без названия"),
                description=vac_data.get("description"),
                key_skills=skills,
                experience=self.EXPERIENCE_CODES.get(vac_data.get("experience", {}).get("id"), "Не указано"),
                salary_from=salary.get("from") if salary else None,
                salary_to=salary.get("to") if salary else None,
                salary_currency=salary.get("currency") if salary else None,
                salary_gross=salary.get("gross") if salary else None,
                region=vac_data.get("area", {}).get("name"),
                url=vac_data.get("alternate_url"),
                status="active",
                published_at=pub_at,
                last_checked_at=datetime.now()
            )
            self.db.add(vacancy)
            self.db.flush()
            self._create_version(vacancy, "created", [])
            return vacancy, True
        else:
            changed = []
            if existing.title != vac_data.get("name"):
                changed.append("title")
                existing.title = vac_data.get("name", "")
            existing.last_checked_at = datetime.now()
            if changed:
                self._create_version(existing, "updated", changed)
                existing.updated_at = datetime.now()
            return existing, False
    
    def _create_version(self, vacancy: Vacancy, change_type: str, fields: List[str]):
        version = VacancyVersion(
            vacancy_id=vacancy.id,
            title=vacancy.title,
            description=vacancy.description,
            key_skills=vacancy.key_skills,
            salary_from=vacancy.salary_from,
            salary_to=vacancy.salary_to,
            status=vacancy.status,
            change_type=change_type,
            changed_fields=fields
        )
        self.db.add(version)
    
    async def parse_and_save(self, keywords: List[str], regions: Optional[List[int]] = None, **params) -> Dict[str, int]:
        stats = {"found": 0, "new": 0, "updated": 0, "errors": 0}
        try:
            vacancies = await self.search_vacancies(keywords=keywords, regions=regions, **params)
            stats["found"] = len(vacancies)
            
            for vac_brief in vacancies:
                try:
                    vac_details = await self.get_vacancy_details(vac_brief["id"])
                    if not vac_details:
                        stats["errors"] += 1
                        continue
                    
                    company = self._parse_company(vac_details.get("employer"))
                    if not company:
                        stats["errors"] += 1
                        continue
                    
                    _, is_new = self._parse_vacancy(vac_details, company)
                    if is_new:
                        stats["new"] += 1
                    else:
                        stats["updated"] += 1
                    
                    self.db.commit()
                except Exception as e:
                    logger.error(f"Ошибка обработки вакансии {vac_brief['id']}: {e}")
                    self.db.rollback()
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            self.db.rollback()
        
        return stats

# ============================================
# КОНЕЦ ФАЙЛА hh_parser.py
# ============================================
