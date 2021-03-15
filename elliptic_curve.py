from galois_field import GF

"""
Attention !!! : Insufficient Operater Priority Infomation
class 'GF' * class 'EC' is not calculated because of circular reference
"""


class EC(object):  # Elliptic Curve
    def __init__(self, x, y, a, b, p):
        if not isinstance(x, GF):
            x = GF(x, p)
        self.x = x
        if not isinstance(y, GF):
            y = GF(y, p)
        self.y = y
        if not isinstance(a, GF):
            a = GF(a, p)
        self.a = a
        if not isinstance(b, GF):
            b = GF(b, p)
        self.b = b
        self.p = p
        if x != 0 and y != 0:
            if (self.y**2) != (self.x**3+self.a*self.x+self.b):
                print("Error : Not in Elliptic Curve")
                print("("+str(x.value)+"," + str(y.value)+")")
                exit()

    def add(self, other):
        if not isinstance(other, type(self)):
            print("Error : Add in Elliptic Curve is only class EC")
            exit()
        if (self.a != other.a or self.b != other.b):
            print("Error : Different Elliptic Curve")
            exit()
        if (self == EC(0, 0, self.a, self.b, self.p)):
            return other
        if (other == EC(0, 0, other.a, other.b, other.p)):
            return self
        if (self.x == other.x):
            if (self.y == other.y):
                if(self.y == 0):
                    return EC(0, 0, self.a, self.b, self.p)
                phi = (3*(self.x**2)+self.a)/(2*self.y)
                x = phi**2-self.x-other.x
                y = phi*(self.x-x)-self.y
                return EC(x, y, self.a, self.b, self.p)
            if (-self.y == other.y):
                return EC(0, 0, self.a, self.b, self.p)
            print("Error : Impossible Point")
            exit()
        phi = (other.y-self.y)/(other.x-self.x)
        x = phi**2-self.x-other.x
        y = phi*(self.x-x)-self.y
        return EC(x, y, self.a, self.b, self.p)

    def mul(self, scalar):
        if isinstance(scalar, GF):
            scalar = scalar.value
        if type(scalar) is not int:
            print("Error : Multiple for EC is not int or Class 'GF'")
            exit()
        bin_scalar = bin(scalar)[3:]
        result = self
        for i in bin_scalar:
            if i == "0":
                result = result+result
            else:
                result = result*2+self
        return result

    def __add__(self, other):
        return self.add(other)

    def __mul__(self, other):
        return self.mul(other)

    def __rmul__(self, other):
        return self.mul(other)

    def __eq__(self, other) -> bool:
        if not isinstance(other, EC):
            print("Error : Unmatch Type EC")
            exit()
        return self.x.value == other.x.value and self.y.value == other.y.value

    def __ne__(self, other) -> bool:
        if not isinstance(other, EC):
            print("Error : Unmatch Type EC")
            exit()
        return self.x.value != other.x.value or self.y.value != other.y.value
