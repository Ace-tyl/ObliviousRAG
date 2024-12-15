"""
This script should be executed before the first execution of server.py
"""

from Crypto.PublicKey import RSA
from Crypto import Random
import time


key_length = 8192

start_time = time.time()
random_generator = Random.new().read
key = RSA.generate(key_length, random_generator)
end_time = time.time()

print("Key generated in {} seconds".format(end_time - start_time))

with open("key.pem", "wb") as f:
    f.write(key.exportKey())
