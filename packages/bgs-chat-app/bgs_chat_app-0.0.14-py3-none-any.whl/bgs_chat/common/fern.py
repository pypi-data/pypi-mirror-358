from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

key = settings.FERNET_KEY


class Fern:
    # This is very similar to great-cms/core/fern.py
    # If we're merging with great-cms, we should investigating using that
    # and avoiding duplication

    def encrypt(conversation_key: str) -> str:
        ciphertext_b = Fernet(key).encrypt(conversation_key.encode("utf-8"))
        return ciphertext_b.decode('utf-8')

    def decrypt(ciphertext: str) -> str:
        try:
            ciphertext_b = Fernet(key).decrypt(ciphertext.encode('utf-8'))
            return ciphertext_b.decode('utf-8')
        except InvalidToken:
            return ''