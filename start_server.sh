#!/bin/bash

# Проверяем, установлен ли Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен. Установите Python3 и попробуйте снова."
    exit 1
fi

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Виртуальное окружение не найдено. Запустите install_debian.sh для установки."
    exit 1
fi

# Запускаем сервер
echo "Запуск сервера..."
python3 server.py 