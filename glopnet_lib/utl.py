
import re
from random import random


class ConstEnumerator(object):
    count = 0
    _name_lookup = {}

    def __init__(self):
        enum_names = self._get_iterable()
        for name in enum_names:
            self._name_lookup[self.count] = name
            setattr(self, name, self.count)
            self.count += 1

    def _get_iterable(self):
        return [name for name in dir(self) if not name.startswith("_") and name[0].isupper()]

    def name_of(self, enum):
        return self._name_lookup[enum]


class _dir_enumerator(ConstEnumerator):
    N = None
    E = None
    S = None
    W = None

    def get_ofst(self, dir):
        if dir == self.N:
            result = (0, -1)
        elif dir == self.E:
            result = (1, 0)
        elif dir == self.S:
            result = (0, 1)
        elif dir == self.W:
            result = (-1, 0)
        else:
            print "INVALID DIR: {}".format(dir)
            result = (0, 0)
        return result


DIR = _dir_enumerator()


def raw_input_gen(prompt=""):
    while True:
        yield raw_input(prompt).lstrip().rstrip()


def will_it_float(input):
    assert input != ""
    return re.match("^(\d+)?\.?(\d+)?$", input) is not None


def will_it_int(input):
    assert input != ""

    if type(input) is int:
        return True

    return re.match("^(\d+)$", input) is not None


def coord_is_valid(coord):
    valid = True
    if coord is None:
        valid = False
    elif not (type(coord) is not tuple or type(coord) is not list):
        valid = False
    elif len(coord) != 2:
        valid = False
    elif not will_it_int(coord[0]) or not will_it_int(coord[1]):
        valid = False
    return valid


def decomp_coord(coord):
    return coord[0], coord[1]


def comp_coord(x, y):
    return x, y


def rand_float(*args):
    assert 0 < len(args) < 3

    if len(args) == 1:
        return random() * args[0]
    else:
        return random() * (args[1] - args[0]) + args[0]


def rand_int(*args):
    assert 0 < len(args) < 3

    if len(args) == 1:
        return int(random() * args[0])
    else:
        return int(random() * (args[1] - args[0])) + args[0]


def rand_int_var(start, variance):
    r = rand_int(start)
    v = rand_int(2 * variance)
    var = v - variance
    return r + var
