from random import randint


def get_verification_code():
    number = randint(0, 9999)
    return "{:0>4}".format(number)
