import re
import base64
from Crypto.Cipher import AES


class StringUtil:
    @staticmethod
    def camel_to_snake(name: str) -> str:
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def encrypt(src: str, key: str) -> str:
        '''key: 32byte'''
        cipher = StringUtil.__make_key(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(src.encode())
        blob = tag + ciphertext
        return base64.urlsafe_b64encode(blob).decode().replace('=', '')

    @staticmethod
    def decrypt(src: str, key: str) -> str | None:
        blob = StringUtil.__b64decode_padded(src)
        tag, ciphertext = blob[:16], blob[16:]
        cipher = StringUtil.__make_key(key=key)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data.decode()

    @staticmethod
    def __make_key(key: str):
        return AES.new(key=base64.b64decode(key), mode=AES.MODE_GCM, nonce=key.encode())

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
