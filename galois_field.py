class GF(object):  # Galois field
    def __init__(self, value, p):
        if (value < 0):
            t = -GF(-value, p)
            value = t.value
            p = t.p
        self.value = value % p
        self.p = p

    def is_GF(self, x):
        if isinstance(x, type(self)):
            if x.p == self.p:
                return x
            else:
                print("Error : Different GF p")
                exit()
        if type(x) is int:
            if x >= 0:
                return GF(x, self.p)
            else:
                return -GF(-x, self.p)
        else:
            print("Error : Type is only int or class 'GF'")
            exit()

    def neg(self):
        return GF(self.p - self.value % self.p, self.p)

    def add(self, other):
        return GF((self.value+other.value) % self.p, self.p)

    def sub(self, other):
        return self+(-other)

    def mul(self, other):
        return GF((self.value*other.value) % self.p, self.p)

    def egcd(x, y):
        c0, c1 = x, y
        a0, a1 = 1, 0
        b0, b1 = 0, 1

        while c1 != 0:
            m = c0 % c1
            q = c0 // c1

            c0, c1 = c1, m
            a0, a1 = a1, (a0 - q * a1)
            b0, b1 = b1, (b0 - q * b1)

        return b0

    def reciprocal(self):
        t = GF.egcd(self.p, self.value)
        return GF(t, self.p)

    def div(self, other):
        t = other.reciprocal()
        return self*t

    def pow(self, other):
        if other >= 0:
            return GF((self.value**other) % self.p, self.p)
        else:
            return 1/GF((self.value**(-other)) % self.p, self.p)

    def __neg__(self):
        self.neg()
        return self.neg()

    def __add__(self, other):
        other = self.is_GF(other)
        return self.add(other)

    def __sub__(self, other):
        other = self.is_GF(other)
        return self.sub(other)

    def __truediv__(self, other):
        other = self.is_GF(other)
        return self.div(other)

    def __radd__(self, other):
        other = self.is_GF(other)
        return other.add(self)

    def __rsub__(self, other):
        other = self.is_GF(other)
        return other.sub(self)

    def __rmul__(self, other):
        other = self.is_GF(other)
        return other.mul(self)

    def __rtruediv__(self, other):
        other = self.is_GF(other)
        return other.div(self)

    def __pow__(self, other):
        if type(other) is int:
            return self.pow(other)

    def __eq__(self, other) -> bool:
        if type(other) is int:
            return self.value == other
        return self.value == other.value and self.p == other.p

    def __ne__(self, other) -> bool:
        if type(other) is int:
            return self.value != other
        return self.value != other.value or self.p != other.p
