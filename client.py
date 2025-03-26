import socket
import threading
import json
from crypto import CryptoManager
import sys

class Client:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.crypto = CryptoManager()
        self.username = None

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            return True
        except:
            print("Не удалось подключиться к серверу")
            return False

    def setup_encryption(self):
        # Получаем публичный ключ сервера
        server_public_key_bytes = self.socket.recv(2048)
        server_public_key = self.crypto.load_public_key(server_public_key_bytes)

        # Генерируем и отправляем сессионный ключ
        session_key = self.crypto.generate_session_key()
        encrypted_session_key = self.crypto.encrypt_session_key(session_key, server_public_key)
        self.socket.send(encrypted_session_key)

    def authenticate(self):
        while True:
            print("\n1. Регистрация")
            print("2. Вход")
            choice = input("Выберите действие (1/2): ")

            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")

            auth_data = {
                'action': 'register' if choice == '1' else 'login',
                'username': username,
                'password': password
            }

            self.socket.send(self.crypto.encrypt_message(json.dumps(auth_data)))
            response = json.loads(self.crypto.decrypt_message(self.socket.recv(2048)))

            if response['status'] == 'success':
                self.username = username
                return True
            else:
                print(f"Ошибка: {response['message']}")

    def receive_messages(self):
        while True:
            try:
                message = self.crypto.decrypt_message(self.socket.recv(2048))
                if message:
                    print(f"\n{message}")
                else:
                    break
            except:
                break
        print("\nСоединение потеряно")

    def send_message(self, message):
        try:
            self.socket.send(self.crypto.encrypt_message(message))
        except:
            print("Ошибка отправки сообщения")

    def start(self):
        if not self.connect():
            return

        self.setup_encryption()
        if not self.authenticate():
            return

        # Запускаем поток для приема сообщений
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        print("\nДобро пожаловать в чат! Для выхода введите 'exit'")
        while True:
            message = input()
            if message.lower() == 'exit':
                break
            self.send_message(message)

        self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        print(f"Подключение к серверу {server_ip}...")
        client = Client(host=server_ip)
    else:
        print("Использование: python client.py <ip-адрес_сервера>")
        print("Пример: python client.py 192.168.1.100")
        sys.exit(1)
    client.start() 