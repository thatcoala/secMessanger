#!/bin/bash

# Проверяем, установлен ли Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен. Установите Python3 и попробуйте снова."
    exit 1
fi

# Проверяем, установлены ли зависимости
if ! python3 -c "import cryptography" &> /dev/null; then
    echo "Устанавливаем зависимости..."
    pip3 install -r requirements.txt
fi

# Запускаем сервер
echo "Запуск сервера..."
python3 server.py 