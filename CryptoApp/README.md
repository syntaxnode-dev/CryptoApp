# Crypto Authentication Lab

## Instructor solve script

The included `solve.py` brute-forces the Base64 ciphertext using the lab's
known-word list.

Run it with the ciphertext as an argument:

```bash
python solve.py 'BASE64_CIPHERTEXT'
```

Or run it without an argument and paste the ciphertext when prompted:

```bash
python solve.py
```

The script derives each candidate AES-128 key as `MD5(word)`, decrypts with
AES-ECB, removes PKCS#7 padding, and accepts only valid JSON containing string
`username` and `password` fields.
