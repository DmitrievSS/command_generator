#!/bin/bash

# Определяем реальный путь к скрипту
if [ -L "$0" ]; then
    # Если скрипт запущен через символическую ссылку
    SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
else
    # Если скрипт запущен напрямую
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# Читаем конфигурацию
CONFIG_FILE="$SCRIPT_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Ошибка: Конфигурационный файл не найден: $CONFIG_FILE"
    exit 1
fi

# Устанавливаем переменные окружения из конфига
export DEEPSEEK_API_URL=$(jq -r '.api_url' "$CONFIG_FILE")
export DEEPSEEK_API_TOKEN=$(jq -r '.api_token' "$CONFIG_FILE")

# Активируем виртуальное окружение
source "$SCRIPT_DIR/venv/bin/activate"

# Запускаем основной скрипт с переданными аргументами
"$SCRIPT_DIR/command_generator.py" "$@" 