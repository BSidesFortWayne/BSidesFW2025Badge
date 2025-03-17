import random

letters = '0123456789'

def generate_random_password(length: int = 12) -> str:
    return ''.join(random.choice(letters) for i in range(length))

