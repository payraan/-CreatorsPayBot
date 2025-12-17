import random
import string

def generate_ref_code():
    """تولید کد پیگیری یکتا مثل CP-105-A9F2"""
    number = random.randint(100, 999)
    letters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CP-{number}-{letters}"
