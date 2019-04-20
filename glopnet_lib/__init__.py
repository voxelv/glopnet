from deterministic_random import DRandom
drandom_inst = DRandom(1234567345)


def drandom(i):
    r_number = drandom_inst.get()
    return r_number % i


def reseed_drandom(seed=None):
    result = drandom_inst.reseed(seed)
    return result
