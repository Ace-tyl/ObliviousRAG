import gmpy2
import random


def string_to_num(s):
    """
    Converts a string to a large number
    :param s: The string to convert
    :return: The converted number
    """
    num = 0
    for char in s.encode('utf-8'):
        num = num * 256 + char
    return num


def num_to_string(num):
    """
    Converts a large number to a string
    :param num: The large number to convert
    :return: The converted string
    """
    s = []
    while num > 0:
        s.append(int(num % 256))
        num = num // 256
    return bytes(reversed(s)).decode('utf-8')


def is_prime(q):
    return gmpy2.is_prime(q)


def generate_primes(n):
    """
    Generate a list of first n odd prime numbers
    :param n: The number of prime numbers to generate
    :return: The list of prime numbers
    """
    primes = [3]  # Initialize the first prime 3
    current_num = 5
    while len(primes) < n:
        if is_prime(current_num):
            primes.append(current_num)
        current_num += 2  # Skip even numbers
    return primes


def generate_coprime_numbers(n, k):
    """
    Generate k numbers coprime to n
    :param n: The number n
    :param k: The number of prime numbers to generate
    :return: coprime numbers list
    """
    coprime_numbers = []
    while len(coprime_numbers) < k:
        number = random.randint(1, n - 1)
        if gmpy2.gcd(number, n) == 1:
            coprime_numbers.append(number)
    return coprime_numbers
