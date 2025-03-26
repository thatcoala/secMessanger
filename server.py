import socket
import threading
import json
import sqlite3
from crypto import CryptoManager
from cryptography.fernet import Fernet

class Server:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = {}  # {client_socket: {'username': str, 'crypto': CryptoManager}}
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect('messenger.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, password TEXT)''')
        conn.commit()
        conn.close()

    def register_user(self, username, password):
        conn = sqlite3.connect('messenger.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (username, password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def authenticate_user(self, username, password):
        conn = sqlite3.connect('messenger.db')
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        return result and result[0] == password

    def handle_client(self, client_socket, address):
        crypto = CryptoManager()
        public_key_bytes = crypto.get_public_key_bytes()
        client_socket.send(public_key_bytes)

        # Получаем зашифрованный сессионный ключ
        encrypted_session_key = client_socket.recv(2048)
        session_key = crypto.decrypt_session_key(encrypted_session_key)
        crypto.fernet = Fernet(session_key)

        # Аутентификация
        auth_data = json.loads(crypto.decrypt_message(client_socket.recv(2048)))
        if auth_data['action'] == 'register':
            if self.register_user(auth_data['username'], auth_data['password']):
                client_socket.send(crypto.encrypt_message(json.dumps({'status': 'success'})))
            else:
                client_socket.send(crypto.encrypt_message(json.dumps({'status': 'error', 'message': 'User exists'})))
                client_socket.close()
                return
        else:  # login
            if self.authenticate_user(auth_data['username'], auth_data['password']):
                client_socket.send(crypto.encrypt_message(json.dumps({'status': 'success'})))
            else:
                client_socket.send(crypto.encrypt_message(json.dumps({'status': 'error', 'message': 'Invalid credentials'})))
                client_socket.close()
                return

        self.clients[client_socket] = {'username': auth_data['username'], 'crypto': crypto}
        self.broadcast_message(f"{auth_data['username']} присоединился к чату")

        while True:
            try:
                message = crypto.decrypt_message(client_socket.recv(2048))
                if message:
                    self.broadcast_message(f"{auth_data['username']}: {message}")
                else:
                    break
            except:
                break

        del self.clients[client_socket]
        client_socket.close()
        self.broadcast_message(f"{auth_data['username']} покинул чат")

    def broadcast_message(self, message):
        for client in self.clients:
            try:
                client.send(self.clients[client]['crypto'].encrypt_message(message))
            except:
                continue

    def start(self):
        print(f"Сервер запущен на {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Новое подключение от {address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

if __name__ == "__main__":
    server = Server()
    server.start() 