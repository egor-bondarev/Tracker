import uuid
import random
import string

def random_data():
    """ Return UUID username. """
    return str(uuid.uuid4())

def custom_string(length = random.randint(1, 10)):
    """ Return random string. """
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
