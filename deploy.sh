#!/bin/bash
set -e
PROJECT_DIR="/var/www/u3487987/data/www/egoroffpython.ru/siteKursor"
VENV_DIR="$PROJECT_DIR/venv"
echo "Переходим в папку проекта..."
cd "$PROJECT_DIR"
echo "Активируем виртуальное окружение..."
source "$VENV_DIR/bin/activate"
echo "Показываем текущую ветку и состояние..."
git status
echo "Подтягиваем изменения из GitHub..."
git pull
echo "Обновляем pip..."
pip install --upgrade pip
echo "Устанавливаем зависимости..."
pip install -r requirements.txt
echo "Проверяем проект..."
python manage.py check
echo "Применяем миграции..."
python manage.py migrate
echo "Собираем статику..."
python manage.py collectstatic --noinput
echo "Деплой завершён."
