@echo off
echo Установка зависимостей для SecMessenger...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Установка завершена!
echo Теперь вы можете запустить client.py
pause 