"Some test helpers"
import random
import string


def random_word(length):
    "Generate random string of length"
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))
