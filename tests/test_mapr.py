from termcolor import colored

from glopnet_lib import drandom, reseed_drandom
from glopnet_lib.map_utl.mapr import GeneratedArea, Coord, GeneratedAreaItem as Gai, GeneratedAreaBoxGenerator, GeneratedAreaLineProbeGenerator as Galpg
from glopnet_lib.utl import DIR


NONE_CHAR = " "
ELECTRICAL_SUBSTATION_CHAR = "#"
ROAD_CHAR = "+"

PASS_STR = colored("PASS", 'green')
FAIL_STR = colored("FAIL", 'red')


def test_true(number, value):
    print("{} {}".format(PASS_STR if value else FAIL_STR, number))


def test_false(number, value):
    test_true(number, not value)


def test_generated_area():
    reseed_drandom()
    cases = [
        {'obj': GeneratedArea(), 'exp': {'valid': False, 'items': None}},
        {'obj': GeneratedArea(0), 'exp': {'valid': True, 'items': []}},
        {'obj': GeneratedArea(height=3, width=4), 'exp': {'valid': True, 'items': [Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai()]}},
        {'obj': GeneratedArea(height=3, width=3), 'exp': {'set': Coord(0, 0), 'val': Gai(char="A"), 'items': [Gai(char="A"), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai()]}},
        {'obj': GeneratedArea(height=3, width=3), 'exp': {'set': Coord(2, 0), 'val': Gai(char="B"), 'items': [Gai(), Gai(), Gai(char="B"), Gai(), Gai(), Gai(), Gai(), Gai(), Gai()]}},
        {'obj': GeneratedArea(height=3, width=3), 'exp': {'set': Coord(0, 2), 'val': Gai(char="C"), 'items': [Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(char="C"), Gai(), Gai()]}},
        {'obj': GeneratedArea(height=3, width=3), 'exp': {'set': Coord(2, 2), 'val': Gai(char="D"), 'items': [Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(), Gai(char="D")]}},
    ]
    for i, case in enumerate(cases):
        if 'valid' in case['exp']:
            success = case['obj'].valid == case['exp']['valid']
            # print "{} valid: {}".format(i, PASS_STR if success else "FAIL")
            test_true("{:03}_{}_valid".format(i, test_generated_area.__name__), success)
        if 'set' in case['exp'] and isinstance(case['exp']['set'], Coord):
            case['obj'].set(case['exp']['set'], case['exp']['val'])

            success = case['obj'].get(case['exp']['set']) == case['exp']['val']
            # print "{} set/get: {}".format(i, PASS_STR if success else "FAIL")
            test_true("{:03}_{}_set/get".format(i, test_generated_area.__name__), success)
        if 'items' in case['exp']:
            success = case['obj'].get_items() == case['exp']['items']
            if not success:
                print("actual: {} not equal to expected: {}".format(case['obj'].get_items(), case['exp']['items']))
            # print "{} items: {}".format(i, PASS_STR if success else "FAIL")
            test_true("{:03}_{}_items".format(i, test_generated_area.__name__), success)
        # print case['obj']


def test_generated_area_box_generator():
    reseed_drandom()
    Gai.default_char = NONE_CHAR
    ga = GeneratedArea(9, 9)
    gbg = GeneratedAreaBoxGenerator(Gai(char=ELECTRICAL_SUBSTATION_CHAR), Coord(1, 1), 7, 7)
    gbg.generate(ga)
    gabg_outline = GeneratedAreaBoxGenerator(Gai(char=ROAD_CHAR), Coord(2, 2), 5, 5, filled=False)
    gabg_outline.generate(ga)
    galpg = Galpg(Gai(char=ROAD_CHAR), Coord(0, 0), direction=DIR.S)
    galpg.generate(ga)
    galpg2 = Galpg(Gai(char=ROAD_CHAR), Coord(0, 4), direction=DIR.E)
    galpg2.generate(ga)
    # print ga
    test_true("000_box_gen", ga.__str__().replace("\n", "\\n") == r"+        \n+####### \n+#+++++# \n+#+###+# \n+++++++++\n+#+###+# \n+#+++++# \n+####### \n+        \n")


def test_generated_area_line_probe_generator():
    reseed_drandom()
    Gai.default_char = NONE_CHAR
    ga = GeneratedArea(width=50, height=50)
    for i in range(16):
        galpg = Galpg(Gai(char=ROAD_CHAR), Coord((i * 3) + 3, 0), direction=DIR.S)
        galpg.generate(ga)
    for i in range(24):
        galpg2 = Galpg(Gai(char=ROAD_CHAR), Coord(0, (i * 2) + 1), direction=DIR.E)
        galpg2.generate(ga)
    # print ga.__str__().replace("\n", "\\n")
    test_true("000_lpg", ga.__str__().replace("\n", "\\n") == r"   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++++++\n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++++++\n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++++++++++++++++++++  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++++++\n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++++++\n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++++++++  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++++++++++++++  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++++++++++++++++++++++++++++++++++++++++++\n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n++++++++++  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n+++++++++++++++++++++++++++++++  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n   +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + \n")


def test_generated_area_line_probe_generator_random():
    reseed_drandom()
    Gai.default_char = NONE_CHAR
    ga_w = 80
    ga_h = 20
    ga = GeneratedArea(width=ga_w, height=ga_h)
    gens = []
    for i in range(10):
        gens.append(Galpg(Gai(char=ROAD_CHAR), Coord(drandom(ga_w), drandom(ga_h)), direction=drandom(4)))
    for g in gens:
        g.generate(ga)
    # print ga.__str__().replace("\n", "\\n")
    test_true("000_lpgr", ga.__str__().replace("\n", "\\n") == r"                                                                               +\n                                                                               +\n                                +                                              +\n                                +                                              +\n                                +                                              +\n                                +                                              +\n                                +                                              +\n                                +                                              +\n     +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n                                +                                              +\n                                +                                  +           +\n+++++++++++++++++++++++++++++++++++++++++++++++++++                +            \n                                ++                                 +            \n                                ++                                 +            \n             +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n                                ++                                 +            \n                                ++                                 +            \n                                ++                                 +    +       \n                                ++                                 +    +       \n                                ++                                 +    +       \n")


def run():
    test_generated_area()
    test_generated_area_box_generator()
    test_generated_area_line_probe_generator()
    test_generated_area_line_probe_generator_random()


if __name__ == '__main__':
    run()
