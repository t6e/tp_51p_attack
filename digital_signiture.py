import hashlib
from galois_field import GF
from elliptic_curve import EC
import random as rand

# Secp256k1
Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
A = 0x0000000000000000000000000000000000000000000000000000000000000000
B = 0x0000000000000000000000000000000000000000000000000000000000000007
P = 2 ** 256 - 2 ** 32 - 977

Order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

G = EC(Gx, Gy, A, B, P)


def sign(message, sec_k):
    e = GF(int(hashlib.sha256(message.encode(
        "utf-8")).hexdigest(), 16), Order)
    k = GF(rand.randint(1, P-1), Order)
    r = GF((G*k).x.value, Order)
    s = (e+r*sec_k)/k
    signiture = (r.value, s.value)
    return signiture


def verificate(message, pub_k, signiture) -> bool:
    r, s = signiture
    if not isinstance(r, GF):
        r = GF(int(r), Order)
    if not isinstance(s, GF):
        s = GF(int(s), Order)
    if not isinstance(pub_k, EC):
        pub_k = EC(int(pub_k[0]), int(pub_k[1]), A, B, P)
    e = GF(int(hashlib.sha256(message.encode(
        "utf-8")).hexdigest(), 16), Order)
    w = 1/s
    u1 = e*w
    u2 = r*w
    x = GF((G*u1.value+pub_k*u2.value).x.value, Order)
    return x.value == r.value


def generate_key():
    sec_k = GF(rand.randint(1, P-1), Order)
    pub_k = G*sec_k
    return (sec_k.value, (pub_k.x.value, pub_k.y.value))


if __name__ == '__main__':
    message = "I know."
    pair_k = generate_key()
    signiture = sign(message=message, sec_k=pair_k[0])
    print(verificate(message, pair_k[1], signiture))
