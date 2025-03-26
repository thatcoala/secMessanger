#!/bin/bash
echo "Установка зависимостей для SecMessenger..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
echo
echo "Установка завершена!"
echo "Теперь вы можете запустить client.py" 