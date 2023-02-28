from datetime import datetime
import pyotp
import base64
from django.conf import settings
from django.core.signing import Signer

signer = Signer()


# This class returns the string needed to generate the key
class GenerateKey:
    @staticmethod
    def encode(key):
        key = str(key) + settings.SECRET_KEY
        key = signer.sign(key)
        key = base64.b32encode(key.encode())
        return key.decode()

    @staticmethod
    def decode(key):
        key = base64.b32decode(key)
        key = signer.unsign(key.decode())
        key = key.replace(settings.SECRET_KEY, '')
        return key

