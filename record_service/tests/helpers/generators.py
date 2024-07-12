import random
import string
from datetime import datetime

def number():
    """ Return random number. """
    return random.randint(10, 1000)

def custom_string(length = random.randint(1, 10)):
    """ Return random string. """
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def timestamp_now():
    """ Return current timestamp. """
    return datetime.now().replace(microsecond=0)
