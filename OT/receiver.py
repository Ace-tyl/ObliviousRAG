import gmpy2
import OT.compute as compute


class Receiver(object):
    def __init__(self, n, k, sigma, bulletin):
        self.n = n
        self.k = k
        self.sigma = sigma
        self.bulletin = bulletin
        nn, e, xe = bulletin
        self.secret = compute.generate_coprime_numbers(nn, k)
        primes = compute.generate_primes(n)
        self.sent = []
        for i in range(k):
            self.sent.append(primes[sigma[i]] * pow(self.secret[i], e, nn) * xe % nn)

    def receive(self, c, received):
        nn, e, xe = self.bulletin
        get = []
        for i in range(self.k):
            temp = (gmpy2.invert(received[i], nn) * self.secret[i]) % nn
            get.append(c[self.sigma[i]] * temp % nn)
        return get
