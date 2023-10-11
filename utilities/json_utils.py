import json
from cryptography.fernet import Fernet
from utilities.keys import ENCRYPTION_KEY

cipher_suite = Fernet(ENCRYPTION_KEY.encode())


def encrypt_data(data):
    """Encrypts the given data using Fernet"""
    plaintext = json.dumps(data).encode()
    ciphertext = cipher_suite.encrypt(plaintext)
    return ciphertext


def decrypt_data(ciphertext):
    """Decrypts the given ciphertext using Fernet"""
    decrypted_data = cipher_suite.decrypt(ciphertext)
    return json.loads(decrypted_data)


def write_to_json(filename, data):
    """Writes encrypted data to a JSON file"""
    with open(filename, "wb") as file:
        encrypted_data = encrypt_data(data)
        file.write(encrypted_data)


def read_from_json(filename):
    """Reads and decrypts data from a JSON file"""
    with open(filename, "rb") as file:
        encrypted_data = file.read()
        data = decrypt_data(encrypted_data)
        return data
