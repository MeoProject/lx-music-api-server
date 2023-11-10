# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: EncryptUtils.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

from Crypto.Cipher import AES, DES
import binascii
import base64

def AESEncrypt(plainText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(plainText, str):
        plainText = plainText.encode('utf-8')
    return cipher.encrypt(pad(plainText))

def AESDecrypt(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(cipherText))

def hexAESDecrypt(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(cipherText, str):
        cipherText = cipherText.encode('utf-8')
    return unpad(cipher.decrypt(binascii.unhexlify(cipherText)))

def base64AESDecrypt(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(cipherText, str):
        cipherText = cipherText.encode('utf-8')
    return unpad(cipher.decrypt(base64.b64decode(cipherText)))

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[len(s) - 1:])]