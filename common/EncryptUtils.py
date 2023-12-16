# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: EncryptUtils.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

from Crypto.Cipher import AES, DES
import binascii
import base64

def createAesEncrypt(plainText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(plainText, str):
        plainText = plainText.encode('utf-8')
    return cipher.encrypt(pad(plainText))

def createAesDecrypt(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(cipherText))

def createAesEncryptByHex(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(cipherText, str):
        cipherText = cipherText.encode('utf-8')
    return unpad(cipher.decrypt(binascii.unhexlify(cipherText)))

def createAesEncryptByBase64(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(cipherText, str):
        cipherText = cipherText.encode('utf-8')
    return unpad(cipher.decrypt(base64.b64decode(cipherText)))

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[len(s) - 1:])]