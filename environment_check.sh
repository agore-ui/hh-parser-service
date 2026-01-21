#!/bin/bash

# ============================================================================
# ENVIRONMENT CHECK SCRIPT v1.0
# Проверка готовности окружения для HH Parser Service
# ============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Счетчики
PASS=0
FAIL=0
WARN=0
TOTAL=0

# Переменные для проверки
DB_USER="hh_parser_user"
DB_NAME="hh_parser"
DB_PASSWORD="change_me_in_production_123456"
PROJECT_DIR="/opt/hh_parser_service"
MIN_PYTHON_VERSION="3.10"
MIN_POSTGRES_VERSION="14"
MIN_REDIS_VERSION="6"

# Функции вывода
print_header() {
    echo ""
    echo -e "${BOLD}г============================================================¬${NC}"
    echo -e "${BOLD}¦  ?? Environment Check for HH Parser Service               ¦${NC}"
    echo -e "${BOLD}L============================================================-${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}${BOLD}???????????????????????????????????????????????????????${NC}"
    echo -e "${BLUE}${BOLD}?? $1${NC}"
    echo -e "${BLUE}${BOLD}???????????????????????????????????????????????????????${NC}"
}

check_pass() {
    echo -e "${GREEN}? PASS:${NC} $1"
    ((PASS++))
    ((TOTAL++))
}

check_fail() {
    echo -e "${RED}? FAIL:${NC} $1"
    ((FAIL++))
    ((TOTAL++))
}

check_warn() {
    echo -e "${YELLOW}??  WARN:${NC} $1"
    ((WARN++))
    ((TOTAL++))
}

check_info() {
    echo -e "${BLUE}??  INFO:${NC} $1"
}

# ============================================================================
# ПРОВЕРКИ
# ============================================================================

print_header

# ----------------------------------------------------------------------------
# 1. СИСТЕМНЫЕ ТРЕБОВАНИЯ
# ----------------------------------------------------------------------------
print_section "1. Системные требования"

# Проверка ОС
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
    
    if [[ "$OS_NAME" == *"Ubuntu"* ]] && [[ "$OS_VERSION" == "22.04" ]]; then
        check_pass "Операционная система: Ubuntu $OS_VERSION"
    elif [[ "$OS_NAME" == *"Ubuntu"* ]]; then
        check_warn "Операционная система: Ubuntu $OS_VERSION (рекомендуется 22.04)"
    else
        check_fail "Операционная система: $OS_NAME $OS_VERSION (требуется Ubuntu)"
    fi
else
    check_fail "Не удалось определить операционную систему"
fi

# Проверка прав root
if [ "$EUID" -eq 0 ]; then
    check_pass "Скрипт запущен от пользователя root"
else
    check_fail "Скрипт должен быть запущен от root"
fi

# Проверка архитектуры
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    check_pass "Архитектура процессора: $ARCH"
else
    check_warn "Архитектура процессора: $ARCH (рекомендуется x86_64)"
fi

# Проверка памяти
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -ge 2048 ]; then
    check_pass "Оперативная память: ${TOTAL_MEM}MB"
else
    check_warn "Оперативная память: ${TOTAL_MEM}MB (рекомендуется минимум 2GB)"
fi

# Проверка свободного места
FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$FREE_SPACE" -ge 10 ]; then
    check_pass "Свободное место на диске: ${FREE_SPACE}GB"
else
    check_warn "Свободное место на диске: ${FREE_SPACE}GB (рекомендуется минимум 10GB)"
fi

# ----------------------------------------------------------------------------
# 2. PYTHON
# ----------------------------------------------------------------------------
print_section "2. Python"

# Проверка установки Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    check_pass "Python установлен: $PYTHON_VERSION"
    
    # Проверка версии Python
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    MIN_MAJOR=$(echo $MIN_PYTHON_VERSION | cut -d. -f1)
    MIN_MINOR=$(echo $MIN_PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -gt "$MIN_MAJOR" ] || ([ "$PYTHON_MAJOR" -eq "$MIN_MAJOR" ] && [ "$PYTHON_MINOR" -ge "$MIN_MINOR" ]); then
        check_pass "Версия Python соответствует требованиям (>= $MIN_PYTHON_VERSION)"
    else
        check_fail "Версия Python $PYTHON_VERSION < $MIN_PYTHON_VERSION"
    fi
else
    check_fail "Python3 не установлен"
fi

# Проверка pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    check_pass "pip установлен: $PIP_VERSION"
else
    check_fail "pip3 не установлен"
fi

# Проверка python3-venv
if dpkg -l | grep -q python3-venv; then
    check_pass "python3-venv установлен"
else
    check_warn "python3-venv не установлен (выполните: apt install python3-venv)"
fi

# Проверка python3-dev
if dpkg -l | grep -q python3-dev; then
    check_pass "python3-dev установлен"
else
    check_warn "python3-dev не установлен (выполните: apt install python3-dev)"
fi

# ----------------------------------------------------------------------------
# 3. POSTGRESQL
# ----------------------------------------------------------------------------
print_section "3. PostgreSQL"

# Проверка установки PostgreSQL
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    check_pass "PostgreSQL установлен: версия $PG_VERSION"
    
    # Проверка версии
    if [ "$PG_VERSION" -ge "$MIN_POSTGRES_VERSION" ]; then
        check_pass "Версия PostgreSQL >= $MIN_POSTGRES_VERSION"
    else
        check_warn "Версия PostgreSQL $PG_VERSION < $MIN_POSTGRES_VERSION"
    fi
else
    check_fail "PostgreSQL не установлен"
fi

# Проверка статуса сервиса
if systemctl is-active --quiet postgresql; then
    check_pass "Сервис PostgreSQL запущен"
else
    check_fail "Сервис PostgreSQL не запущен"
fi

# Проверка автозапуска
if systemctl is-enabled --quiet postgresql; then
    check_pass "PostgreSQL включен в автозапуск"
else
    check_warn "PostgreSQL не включен в автозапуск"
fi

# Проверка порта
if netstat -tln | grep -q ":5432"; then
    check_pass "PostgreSQL слушает на порту 5432"
else
    check_fail "PostgreSQL не слушает на порту 5432"
fi

# Проверка существования пользователя БД
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    check_pass "Пользователь БД '$DB_USER' существует"
else
    check_fail "Пользователь БД '$DB_USER' не существует"
fi

# Проверка существования БД
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    check_pass "База данных '$DB_NAME' существует"
else
    check_fail "База данных '$DB_NAME' не существует"
fi

# Проверка подключения к БД
if PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null; then
    check_pass "Подключение к БД '$DB_NAME' работает"
else
    check_fail "Не удается подключиться к БД '$DB_NAME'"
fi

# Проверка конфигурации pg_hba.conf
PG_HBA_FILE=$(sudo -u postgres psql -tAc "SHOW hba_file")
if [ -f "$PG_HBA_FILE" ]; then
    if grep -q "127.0.0.1.*md5\|127.0.0.1.*scram-sha-256" "$PG_HBA_FILE"; then
        check_pass "pg_hba.conf настроен для IPv4 подключений"
    else
        check_warn "pg_hba.conf может требовать настройки для IPv4"
    fi
    
    if grep -q "::1.*md5\|::1.*scram-sha-256" "$PG_HBA_FILE"; then
        check_pass "pg_hba.conf настроен для IPv6 подключений"
    else
        check_warn "pg_hba.conf может требовать настройки для IPv6"
    fi
fi

# ----------------------------------------------------------------------------
# 4. REDIS
# ----------------------------------------------------------------------------
print_section "4. Redis"

# Проверка установки Redis
if command -v redis-cli &> /dev/null; then
    REDIS_VERSION=$(redis-cli --version | awk '{print $2}' | cut -d= -f2 | cut -d. -f1)
    check_pass "Redis установлен: версия $REDIS_VERSION.x"
    
    # Проверка версии
    if [ "$REDIS_VERSION" -ge "$MIN_REDIS_VERSION" ]; then
        check_pass "Версия Redis >= $MIN_REDIS_VERSION"
    else
        check_warn "Версия Redis $REDIS_VERSION < $MIN_REDIS_VERSION"
    fi
else
    check_fail "Redis не установлен (выполните: apt install redis-server)"
fi

# Проверка статуса сервиса
if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
    check_pass "Сервис Redis запущен"
else
    check_fail "Сервис Redis не запущен"
fi

# Проверка подключения
if redis-cli ping &> /dev/null; then
    check_pass "Подключение к Redis работает"
else
    check_fail "Не удается подключиться к Redis"
fi

# Проверка порта
if netstat -tln | grep -q ":6379"; then
    check_pass "Redis слушает на порту 6379"
else
    check_warn "Redis не слушает на порту 6379"
fi

# ----------------------------------------------------------------------------
# 5. GIT
# ----------------------------------------------------------------------------
print_section "5. Git"

# Проверка установки Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    check_pass "Git установлен: $GIT_VERSION"
else
    check_fail "Git не установлен (выполните: apt install git)"
fi

# Проверка конфигурации Git
if git config --global user.name &> /dev/null; then
    GIT_USER=$(git config --global user.name)
    check_pass "Git user.name настроен: $GIT_USER"
else
    check_warn "Git user.name не настроен (выполните: git config --global user.name 'Your Name')"
fi

if git config --global user.email &> /dev/null; then
    GIT_EMAIL=$(git config --global user.email)
    check_pass "Git user.email настроен: $GIT_EMAIL"
else
    check_warn "Git user.email не настроен (выполните: git config --global user.email 'your@email.com')"
fi

# Проверка SSH ключей
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    check_pass "SSH ключи найдены"
    
    # Проверка подключения к GitHub
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        check_pass "SSH подключение к GitHub работает"
    else
        check_warn "SSH подключение к GitHub не настроено"
    fi
else
    check_warn "SSH ключи не найдены (выполните:
