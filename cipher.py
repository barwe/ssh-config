import base64
import hashlib
import secrets
from Crypto.Cipher import AES


def pad(text: str):
    num_bytes = len(text.encode())
    return text + (16 - num_bytes % 16) * chr(16 - num_bytes % 16)


def unpad(data: bytes):
    return data[: -ord(data[len(data) - 1 :])]


class AESCipher:
    def __init__(self, key: bytes) -> None:
        self.key = key

    def encrypt(self, raw: str):
        raw = pad(raw).encode()
        iv = secrets.token_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode()

    def decrypt(self, b64str: str):
        data = base64.b64decode(b64str)
        iv = data[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data[16:])).decode()

    @staticmethod
    def create_with_password(password: str):
        hash_object = hashlib.sha256()
        hash_object.update(password.encode("utf-8"))
        hex_hash = hash_object.hexdigest()
        if len(hex_hash) < 16:
            hex_hash = hex_hash.ljust(16, "0")
        if len(hex_hash) > 16:
            hex_hash = hex_hash[:16]
        key = hex_hash.encode()
        return AESCipher(key)
