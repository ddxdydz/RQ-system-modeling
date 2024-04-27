from math import log
from random import random


def get_exponent_time(intensity_factor):
    return -log(random()) / intensity_factor  # экспоненциальное время
