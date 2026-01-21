# HH Parser Service

## Описание проекта

HH Parser Service - это сервис для парсинга вакансий с платформы HeadHunter (hh.ru) с фокусом на вакансии в сфере микроэлектроники и телеком-оборудования.

### Основные возможности

- **Парсинг вакансий** из HH.ru API по заданным критериям
- **Сохранение данных** в PostgreSQL с использованием SQLAlchemy
- **RESTful API** для управления вакансиями, компаниями и запуска парсинга
- **Фильтрация** по ключевым словам, регионам и другим параметрам
- **Аналитика** по собранным вакансиям
- **CORS поддержка** для интеграции с фронтенд-приложениями

### Целевые специализации

**Области:**
- Микроэлектроника
- Телеком-оборудование

**Роли:**
- Инженер-схемотехник
- Тополог (PCB)
- ASIC Design Engineer
- RTL Developer
- FPGA Developer
- Инженер по фотонике
- Firmware Engineer

**Технологии:**
- **Chip Design & FPGA:** Verilog, SystemVerilog, VHDL, UVM, Xilinx Vivado, Intel Quartus, Cadence, Mentor Graphics, RISC-V, ARM
- **Topography & Scripts:** Cadence SKILL (Lisp), TCL scripting, P-CAD, Altium Designer, DRM, LVS

## Технологический стек

- **Backend:** FastAPI (Python 3.8+)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Кеширование:** Redis (опционально)
- **API:** HeadHunter API
- **Валидация:** Pydantic
- **Миграции:** Alembic

## Структура проекта

```
hh-parser-service/
├── app/
│   ├── api/
│   │   ├── __init__.py          # API роутер
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── vacancies.py     # Эндпоинты для вакансий
│   │       ├── companies.py     # Эндпоинты для компаний
│   │       └── parser.py        # Эндпоинты для парсинга
│   ├── core/
│   │   └── __init__.py
│   ├── exceptions/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hh_parser.py         # Основной парсер HH.ru
│   │   └── db_service.py        # Сервисы работы с БД
│   ├── tests/
│   │   ├── integration/
│   │   └── unit/
│   ├── utils/
│   ├── __init__.py
│   ├── database.py              # Подключение к БД
│   ├── models.py                # SQLAlchemy модели
│   └── schemas.py               # Pydantic схемы
├── config.py                     # Конфигурация
├── main.py                       # Точка входа
├── requirements.txt
└── README.md
```

## Установка и настройка

### Требования

- Python 3.8+
- PostgreSQL 12+
- Redis (опционально)

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/agore-ui/hh-parser-service.git
cd hh-parser-service
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
# Application
APP_NAME="HH Parser Service"
APP_ENV=development

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hh_parser

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Шаг 5: Инициализация базы данных

```bash
# Создание БД
psql -U postgres -c "CREATE DATABASE hh_parser;"

# Применение миграций (если используется Alembic)
alembic upgrade head
```

### Шаг 6: Запуск сервиса

```bash
python main.py
```

Или с помощью uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Документация

После запуска сервиса, документация API доступна по адресам:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Основные эндпоинты

#### Вакансии

```
GET    /api/v1/vacancies          # Получить список вакансий
GET    /api/v1/vacancies/{id}     # Получить вакансию по ID
GET    /api/v1/vacancies/hh/{id}  # Получить вакансию по HH ID
POST   /api/v1/vacancies          # Создать вакансию
PUT    /api/v1/vacancies/{id}     # Обновить вакансию
DELETE /api/v1/vacancies/{id}     # Удалить вакансию

GET    /api/v1/vacancies/filters          # Получить фильтры
POST   /api/v1/vacancies/filters          # Создать фильтр
GET    /api/v1/vacancies/analytics        # Получить аналитику
```

#### Компании

```
GET    /api/v1/companies          # Получить список компаний
GET    /api/v1/companies/{id}     # Получить компанию по ID
GET    /api/v1/companies/hh/{id}  # Получить компанию по HH ID
POST   /api/v1/companies          # Создать компанию
PUT    /api/v1/companies/{id}     # Обновить компанию
DELETE /api/v1/companies/{id}     # Удалить компанию
```

#### Парсинг

```
POST   /api/v1/parser/parse       # Запустить парсинг
GET    /api/v1/parser/search      # Поиск без сохранения
GET    /api/v1/parser/vacancy/{id} # Детали вакансии из HH
GET    /api/v1/parser/company/{id} # Информация о компании из HH
```

### Примеры использования

#### Запуск парсинга

```bash
curl -X POST "http://localhost:8000/api/v1/parser/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["FPGA Developer", "RTL Engineer"],
    "regions": [1, 2]
  }'
```

#### Получение списка вакансий

```bash
curl -X GET "http://localhost:8000/api/v1/vacancies?skip=0&limit=10"
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# Юнит-тесты
pytest app/tests/unit/

# Интеграционные тесты
pytest app/tests/integration/

# С покрытием кода
pytest --cov=app --cov-report=html
```

## Разработка

### Добавление новых функций

1. Создайте новую ветку: `git checkout -b feature/your-feature`
2. Внесите изменения
3. Добавьте тесты
4. Запустите тесты: `pytest`
5. Создайте Pull Request

### Code Style

Проект следует PEP 8 и использует:
- `black` для форматирования
- `flake8` для линтинга
- `mypy` для проверки типов

```bash
# Форматирование
black app/

# Линтинг
flake8 app/

# Проверка типов
mypy app/
```

## Развёртывание

### Docker

```bash
# Сборка образа
docker build -t hh-parser-service .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env hh-parser-service
```

### Docker Compose

```bash
docker-compose up -d
```

## Лицензия

MIT License

## Авторы

- Ваше имя (@agore-ui)

## Контакты

По вопросам и предложениям создавайте Issue в репозитории.

## Благодарности

- HeadHunter API за предоставление данных
- FastAPI за отличный фреймворк
- Сообщество разработчиков
