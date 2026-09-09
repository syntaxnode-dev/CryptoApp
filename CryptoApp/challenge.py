
import base64, hashlib, json, secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

WORDS=["dragon","monkey","shadow","letmein","football","sunshine","princess","welcome","password","trustno1"]

def key(word): return hashlib.md5(word.encode()).digest()

user=f"user_{secrets.token_hex(3)}"
pwd=secrets.token_urlsafe(8)
word=secrets.choice(WORDS)
pt=json.dumps({"username":user,"password":pwd}).encode()
ct=base64.b64encode(AES.new(key(word),AES.MODE_ECB).encrypt(pad(pt,16))).decode()

print("=== Authentication Challenge ===")
print("Ciphertext:\n",ct)
while True:
    u=input("Username: ")
    p=input("Password: ")
    if u==user and p==pwd:
        print("Authenticated!\nFLAG{authentication_successful}")
        break
    print("Invalid credentials.")
