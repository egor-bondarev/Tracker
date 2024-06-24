""" Generator for test data. """

import random
import string
import uuid

def username():
    """ Return UUID username. """
    return str(uuid.uuid4())

def custom_string(length = random.randint(1, 10)):
    """ Return random string. """
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def number():
    """ Return random number. """
    return random.randint(10, 1000)

def number_one_symbol():
    """ Return one symbol random number. """
    return random.randint(0, 9)

def string_and_num():
    """ Return mixed random string by letters and digits. """
    chars = string.ascii_letters + string.digits
    length = random.randint(2, 10)
    return ''.join(random.choice(chars) for _ in range(length))
