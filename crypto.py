from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64
import os

class CryptoManager:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.fernet = None

    def get_public_key_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def load_public_key(self, key_bytes):
        return serialization.load_pem_public_key(key_bytes)

    def generate_session_key(self):
        session_key = Fernet.generate_key()
        self.fernet = Fernet(session_key)
        return session_key

    def encrypt_session_key(self, session_key, recipient_public_key):
        encrypted_key = recipient_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key

    def decrypt_session_key(self, encrypted_key):
        return self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_message(self, message):
        if not self.fernet:
            raise ValueError("Session key not initialized")
        return self.fernet.encrypt(message.encode())

    def decrypt_message(self, encrypted_message):
        if not self.fernet:
            raise ValueError("Session key not initialized")
        return self.fernet.decrypt(encrypted_message).decode()

    def hash_password(self, password):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        return base64.b64encode(digest.finalize()).decode() 