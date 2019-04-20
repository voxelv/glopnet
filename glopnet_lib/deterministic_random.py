
from random import Random


class DRandom:
    def __init__(self, seed):
        self.original_seed = seed
        self._r = Random(seed)
        self.val = seed

    def lfsr_get(self):
        bits = bin(self.val)[2:]
        while len(bits) < 31:
            bits = '0' + bits
        bit31 = eval("0b" + (bits[-31]))
        bit28 = eval("0b" + (bits[-28]))
        newbit = "0" if int(bit31 ^ bit28) == 1 else "1"
        bits = bits[1:] + newbit
        self.val = int(bits, 2)
        return self.val

    def get(self):
        result = self._r.randrange(0, 2**64)
        return result

    def reseed(self, seed=None):
        if seed is not None:
            self._r.seed(seed)
        else:
            self._r.seed(self.original_seed)
