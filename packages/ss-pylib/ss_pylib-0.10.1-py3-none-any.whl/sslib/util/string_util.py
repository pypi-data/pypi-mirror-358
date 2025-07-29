import re
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class StringUtil:
    ASSOCIATED = b'header'

    @staticmethod
    def camel_to_snake(name: str) -> str:
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def encrypt(src: str, key: str) -> str:
        '''key: 32byte'''
        nonce, cipher = StringUtil.__make_key(key=key)
        encrypted = cipher.encrypt(nonce=nonce, data=src.encode(), associated_data=StringUtil.ASSOCIATED)
        return base64.urlsafe_b64encode(encrypted).decode().replace('=', '')

    @staticmethod
    def decrypt(src: str, key: str) -> str | None:
        encrypted = StringUtil.__b64decode_padded(src)
        nonce, cipher = StringUtil.__make_key(key=key)
        decrypted = cipher.decrypt(nonce=nonce, data=encrypted, associated_data=StringUtil.ASSOCIATED)
        return decrypted.decode()

    @staticmethod
    def __make_key(key: str):
        nonce = base64.b64decode(key)
        return nonce, AESGCM(key=nonce)

    @staticmethod
    def __b64decode_padded(data_b64: str) -> bytes:
        '''Base64 문자열을 디코딩할 때, 패딩(=)이 모자라면 채워주고 디코딩'''
        s = data_b64.strip()
        # 길이를 4의 배수로 만들어 줄 패딩 개수 계산
        pad_len = (-len(s)) % 4
        if pad_len:
            s += "=" * pad_len
        return base64.urlsafe_b64decode(s)


if __name__ == '__main__':
    KEY = '12345678901234567890123456789012'
    encrypted = StringUtil.encrypt('암호화', KEY)
    print(f'암호화: {encrypted}')
    decrypted = StringUtil.decrypt(encrypted, KEY)
    print(f'복호화: {decrypted}')
