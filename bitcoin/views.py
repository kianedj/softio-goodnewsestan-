from django.shortcuts import render
from config.settings import BASE_DIR
# Create your views here.
import os
import hashlib
import qrcode

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()


def ripemd160(x):
    d = hashlib.new("ripemd160")
    d.update(x)
    return d.digest()


def b58(data):
    B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    if data[0] == 0:
        return "1" + b58(data[1:])

    x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
    ret = ""
    while x > 0:
        ret = B58[x % 58] + ret
        x = x // 58

    return ret


class Point:
    def __init__(self,
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
        p=2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1):
        self.x = x
        self.y = y
        self.p = p

    def __add__(self, other):
        return self.__radd__(other)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __rmul__(self, other):
        n = self
        q = None

        for i in range(256):
            if other & (1 << i):
                q = q + n
            n = n + n

        return q

    def __radd__(self, other):
        if other is None:
            return self
        x1 = other.x
        y1 = other.y
        x2 = self.x
        y2 = self.y
        p = self.p

        if self == other:
            l = pow(2 * y2 % p, p-2, p) * (3 * x2 * x2) % p
        else:
            l = pow(x1 - x2, p-2, p) * (y1 - y2) % p

        newX = (l ** 2 - x2 - x1) % p
        newY = (l * x2 - l * newX - y2) % p

        return Point(newX, newY)

    def toBytes(self):
        x = self.x.to_bytes(32, "big")
        y = self.y.to_bytes(32, "big")
        return b"\x04" + x + y


def getPublicKey(privkey):
    SPEC256k1 = Point()
    pk = int.from_bytes(privkey, "big")
    hash160 = ripemd160(sha256((SPEC256k1 * pk).toBytes()))
    address = b"\x00" + hash160

    address = b58(address + sha256(sha256(address))[:4])
    return address


def getWif(privkey):
    wif = b"\x80" + privkey
    wif = b58(wif + sha256(sha256(wif))[:4])
    return wif

def makeqrcode(publickey,privkey):
    qr = qrcode.QRCode(
        # integer from 1 to 40 that controls the size of the QR Code
        version=1,

        # error_correction parameter controls the error correction used for the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        
        # box_size parameter controls how many pixels each “box” of the QR code is.
        box_size=10,
        
        # border parameter controls how many boxes thick the border should be.
        # the default is 4, which is the minimum
        border=4,
    )

    tobeqr = [publickey,privkey]
    name = 'public_key.png'
    # add your text here
    for item in tobeqr:
        qr.add_data(item)
        qr.make(fit=True)
        

        # change the colors of the QR code
        img = qr.make_image(fill_color="gold", back_color="black")

        # name the file and save it
        img.save(str(BASE_DIR.joinpath('static/images/{}'.format(name))))
        qr.clear()
        name = 'private_key.png'
#str(BASE_DIR.joinpath('static/images/{}'.format(str(name +'_'+item[-4:])+'.png')))
def BitcoinView(request):
    randomBytes = os.urandom(32)
    public_key = getPublicKey(randomBytes)
    private_key = getWif(randomBytes)
    makeqrcode(public_key,private_key)
    context = {
        'public_key': public_key,
        'private_key': str(private_key),
        'public_key_img': 'images/public_key_' + str(public_key[-4:]) + '.png',
        'private_key_img': str(BASE_DIR.joinpath('static/images/{}'.format('private_key.png'))),
    }
    return render(request, 'bitcoin.html', context=context)