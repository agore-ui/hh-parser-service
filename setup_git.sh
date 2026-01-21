#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Настройка Git...${NC}"
echo ""

# Проверка установки Git
if ! command -v git &> /dev/null; then
    echo "Git не установлен. Устанавливаю..."
    apt update -qq && apt install -y git
fi

# Настройка Git config
echo -e "${BLUE}📝 Настройка Git конфигурации...${NC}"

read -p "Введите ваше имя для Git: " GIT_NAME
read -p "Введите ваш email для Git: " GIT_EMAIL

git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
git config --global init.defaultBranch main

echo -e "${GREEN}✅ Git настроен:${NC}"
echo "   Имя: $(git config --global user.name)"
echo "   Email: $(git config --global user.email)"
echo ""

# Инициализация репозитория
echo -e "${BLUE}🎯 Инициализация Git репозитория...${NC}"
cd /opt/hh_parser_service

if [ -d .git ]; then
    echo -e "${YELLOW}⚠️  Git репозиторий уже существует${NC}"
else
    git init
    echo -e "${GREEN}✅ Git репозиторий инициализирован${NC}"
fi

git branch -M main

echo ""
echo -e "${GREEN}🎉 Git настройка завершена!${NC}"
