import gmpy2
import random
from Crypto.PublicKey import RSA
import OT.compute as compute


def rand_generator(nn):
    x = random.randint(1, nn)
    while pow(x, 4, nn) == 1 or gmpy2.gcd(x, nn) != 1:
        x = random.randint(1, nn)
    return x


recorded_power_value = {}


def get_recorded_power(p, d, nn):
    if (p, d, nn) in recorded_power_value:
        return recorded_power_value[(p, d, nn)]
    result = pow(p, d, nn)
    recorded_power_value[(p, d, nn)] = result
    return result


class Sender(object):
    def __init__(self, msg, n):
        key = RSA.importKey(open('key.pem').read())  # Read the key
        nn = key.n
        e = key.e
        self.d = key.d
        self.x = rand_generator(nn)
        self.bulletin = [nn, e, pow(self.x, e, nn)]
        primes = compute.generate_primes(n)
        self.c = []
        for i in range(n):
            self.c.append(msg[i] * self.x * get_recorded_power(primes[i], self.d, nn) % nn)

    def send(self, received):
        nn, e, xe = self.bulletin
        sent = []
        for i in range(len(received)):
            sent.append(get_recorded_power(received[i], self.d, nn))
        return self.c, sent
