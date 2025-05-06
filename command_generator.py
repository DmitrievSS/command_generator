#!/usr/bin/env python3
import sys
import json
import requests
import os
from typing import List, Dict
import urllib3
import subprocess
import argparse

# Отключаем предупреждения о небезопасном SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def log(message: str, enable_logging: bool = False):
    """Выводит сообщение в stderr только если включено логирование"""
    if enable_logging:
        print(message, file=sys.stderr)

def generate_command(description: str, enable_logging: bool = False) -> str:
    # Получаем URL API из переменной окружения
    api_url = os.getenv("DEEPSEEK_API_URL")
    if not api_url:
        print("Ошибка: Не установлена переменная окружения DEEPSEEK_API_URL", file=sys.stderr)
        return ""
    
    url = api_url
    
    # Получаем токен из переменной окружения
    api_token = os.getenv("DEEPSEEK_API_TOKEN")
    if not api_token:
        print("Ошибка: Не установлена переменная окружения DEEPSEEK_API_TOKEN", file=sys.stderr)
        return ""
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Читаем последние 10 строк из файла истории zsh
    history_file = os.path.expanduser("~/.zsh_history")
    try:
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Читаем все строки и берем последние 10
            history = f.readlines()[-10:]
    except Exception as e:
        print(f"Ошибка при чтении истории: {e}", file=sys.stderr)
        history = []
    
    prompt = f"""На основе следующего описания и истории команд, сгенерируйте bash-команду.
Описание: {description}

История последних команд:
{json.dumps(history, indent=2, ensure_ascii=False)}

Пожалуйста, сгенерируйте только bash-команду без дополнительных пояснений."""

    # Логируем промт
    log("=== Отправляемый промт ===", enable_logging)
    log(prompt, enable_logging)
    log("========================", enable_logging)

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "deepseek-chat-v3"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        response_data = response.json()
        
        # Логируем ответ от API
        log("\n=== Ответ от API ===", enable_logging)
        log(json.dumps(response_data, indent=2, ensure_ascii=False), enable_logging)
        log("===================", enable_logging)
        
        return response_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}", file=sys.stderr)
        return ""

def main():
    parser = argparse.ArgumentParser(description='Генерация bash-команд на основе описания')
    parser.add_argument('--log', action='store_true', help='Включить логирование')
    parser.add_argument('description', nargs=argparse.REMAINDER, help='Описание команды')
    
    args = parser.parse_args()
    description = ' '.join(args.description)
    
    command = generate_command(description, args.log)
    if command:
        print(command)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 