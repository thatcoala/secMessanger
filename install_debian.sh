#!/bin/bash

echo "Установка необходимых пакетов системы..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "Создание виртуального окружения..."
python3 -m venv venv

echo "Активация виртуального окружения..."
source venv/bin/activate

echo "Установка зависимостей проекта..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Установка завершена!"
echo "Для запуска сервера используйте: ./start_server.sh"
echo "Для активации виртуального окружения используйте: source venv/bin/activate" 