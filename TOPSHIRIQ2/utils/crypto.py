import os
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import NoEncryption
import secrets

# RSA key generation, signing and verification

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_bytes, public_bytes


def sign_message(private_bytes, message: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(private_bytes, password=None)
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature


def verify_signature(public_bytes, message: bytes, signature: bytes) -> bool:
    public_key = serialization.load_pem_public_key(public_bytes)
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

# HMAC SHA256

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).hexdigest()

# Simple Shamir-like split (not cryptographically complete) for demo
# We implement a simple (2-of-3) split using XOR shares for demonstration

def _modinv(a, p):
    # modular inverse using extended Euclid
    a = a % p
    if a == 0:
        raise ZeroDivisionError('No inverse')
    # extended gcd
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        hm, lm = lm, nm
        high, low = low, new
    return lm % p


def split_secret_shares(secret: bytes):
    """Split secret into 3 shares with threshold 2 using Shamir over prime 257.

    Each share is encoded as: 1 byte x index (1..3) followed by for each secret byte a 2-byte big-endian
    value representing f(x) mod 257. The returned shares are raw bytes.
    """
    p = 257
    n = 3
    shares = []
    # choose for each byte a random coefficient a (degree 1 polynomial f(x)=s + a*x mod p)
    coeffs = [secrets.randbelow(p) for _ in range(len(secret))]
    for x in range(1, n + 1):
        out = bytearray()
        out.append(x)
        for i, s in enumerate(secret):
            a = coeffs[i]
            y = (s + a * x) % p
            out.extend(y.to_bytes(2, 'big'))
        shares.append(bytes(out))
    return shares


def recover_secret_from_shares(shares):
    """Recover secret from at least 2 shares produced by split_secret_shares.

    shares: iterable of raw share bytes as returned by split_secret_shares.
    Returns the original secret bytes.
    """
    p = 257
    shares = list(shares)
    if len(shares) < 2:
        raise ValueError('Kamida 2 ulush kerak')
    # parse shares
    parsed = []
    for sh in shares:
        if len(sh) < 1:
            raise ValueError('Noto\'g\'ri ulush')
        x = sh[0]
        ys = []
        data = sh[1:]
        if len(data) % 2 != 0:
            raise ValueError('Noto\'g\'ri ulush uzunligi')
        for i in range(0, len(data), 2):
            ys.append(int.from_bytes(data[i:i+2], 'big'))
        parsed.append((x, ys))

    # ensure all shares have same length
    length = len(parsed[0][1])
    for _, ys in parsed:
        if len(ys) != length:
            raise ValueError('Ulushlar turlicha uzunlikda')

    # Use first two shares to reconstruct (threshold 2)
    x1, y1 = parsed[0]
    x2, y2 = parsed[1]
    secret = bytearray()
    denom = (x2 - x1) % p
    inv = _modinv(denom, p)
    for i in range(length):
        yy1 = y1[i]
        yy2 = y2[i]
        a = ((yy2 - yy1) * inv) % p
        s = (yy1 - a * x1) % p
        if s < 0 or s > 255:
            # if for some reason out of 0-255 range, raise
            raise ValueError('Qayta tiklangan bayt 0-255 oralig\'ida emas')
        secret.append(s)
    return bytes(secret)
