#!/bin/bash

# ============================================================================
# PRE-DEPLOYMENT CHECK - Проверка перед загрузкой на GitHub
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

PASS=0
FAIL=0
WARN=0

print_header() {
    echo -e "${BOLD}г============================================================¬${NC}"
    echo -e "${BOLD}¦  ?? Pre-Deployment Check for GitHub Upload                ¦${NC}"
    echo -e "${BOLD}L============================================================-${NC}"
    echo ""
}

check_pass() {
    echo -e "${GREEN}?${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}?${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}??${NC} $1"
    ((WARN++))
}

print_header

echo -e "${BLUE}?? Проверка 1: Права доступа${NC}"
if [ "$EUID" -eq 0 ]; then
    check_pass "Запущено от root"
else
    check_fail "Требуется запуск от root"
    exit 1
fi

echo ""
echo -e "${BLUE}?? Проверка 2: Директория проекта${NC}"
if [ -d "/opt/hh_parser_service" ]; then
    check_pass "Директория /opt/hh_parser_service существует"
    cd /opt/hh_parser_service
else
    check_fail "Директория /opt/hh_parser_service не найдена"
    echo "Создаю директорию..."
    mkdir -p /opt/hh_parser_service
    cd /opt/hh_parser_service
    check_pass "Директория создана"
fi

echo ""
echo -e "${BLUE}?? Проверка 3: Git${NC}"
if command -v git &> /dev/null; then
    check_pass "Git установлен: $(git --version | awk '{print $3}')"
else
    check_fail "Git не установлен"
    echo "Устанавливаю Git..."
    apt update -qq && apt install -y git
    check_pass "Git установлен"
fi

echo ""
echo -e "${BLUE}?? Проверка 4: PostgreSQL${NC}"
if PGPASSWORD='change_me_in_production_123456' psql -h 127.0.0.1 -U hh_parser_user -d hh_parser -c "SELECT 1" &> /dev/null; then
    check_pass "PostgreSQL подключение работает"
else
    check_fail "PostgreSQL подключение не работает"
fi

echo ""
echo -e "${BLUE}?? Проверка 5: Файл .env${NC}"
if [ -f "/opt/hh_parser_service/.env" ]; then
    check_pass "Файл .env существует"
    if grep -q "DATABASE_URL" /opt/hh_parser_service/.env; then
        check_pass ".env содержит DATABASE_URL"
    else
        check_warn ".env не содержит DATABASE_URL"
    fi
else
    check_warn "Файл .env отсутствует (будет создан)"
fi

echo ""
echo -e "${BLUE}?? Проверка 6: SSH ключи для GitHub${NC}"
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    check_pass "SSH ключи найдены"
    
    # Проверка подключения к GitHub
    if timeout 5 ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        check_pass "SSH подключение к GitHub работает"
    else
        check_warn "SSH подключение к GitHub не проверено (может потребоваться настройка)"
    fi
else
    check_warn "SSH ключи не найдены (будут созданы)"
fi

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${GREEN}? Пройдено: $PASS${NC}"
echo -e "${RED}? Ошибок: $FAIL${NC}"
echo -e "${YELLOW}??  Предупреждений: $WARN${NC}"
echo -e "${BOLD}============================================================${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}${BOLD}?? Система готова к загрузке на GitHub!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}${BOLD}? Обнаружены критические ошибки. Исправьте их перед продолжением.${NC}"
    exit 1
fi
EOF


