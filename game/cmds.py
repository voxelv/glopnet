
from glopnet_lib.utl import will_it_float, decomp_coord, comp_coord, will_it_int
import const as c
from gamestate import GlopnetGamestate


def get_gamestate(k):
    """
    Gets the gamestate out of the dictionary k and verifies it.
    :param k: The keyword argument dictionary
    :type k: dict
    :return: The gamestate
    :rtype: GlopnetGamestate
    """
    if c.GAMESTATE in k and k[c.GAMESTATE] and type(k[c.GAMESTATE]) is GlopnetGamestate and k[c.GAMESTATE].is_valid():
        result = k[c.GAMESTATE]
    else:
        print("Invalid gamestate!")
        result = None
    return result


def get_loc(gamestate):
    return decomp_coord(gamestate.current_loc)


def cmd_map(cmd="map", *args, **kwargs):
    gamestate = get_gamestate(kwargs)
    print(gamestate.map)


def cmd_look(cmd="look", *args, **kwargs):
    def local_print(f):
        if not kwargs.get('no_print', False):
            print(f)

    gamestate = get_gamestate(kwargs)
    if len(args) == 0:
        x, y = get_loc(gamestate)
        local_print("You're at a {}.".format(gamestate.map.get(x, y).name))
    elif len(args) == 1:
        arg0 = args[0]
        if arg0 in c.DIRECTIONS_AROUND:
            x, y = get_loc(gamestate)
            look_x, look_y = decomp_coord(c.DIR_OFFSETS[arg0])
            new_x, new_y = x + look_x, y + look_y
            if gamestate.can_explore(new_x, new_y):
                gamestate.explore_coord(new_x, new_y)
                tile = gamestate.map.get(new_x, new_y)
                local_print("To the {} you see a {}.".format(c.DIR_DESCRIPTION[arg0], tile.name))
            else:
                local_print("That way is out of bounds.")
        elif arg0 == "around":
            x, y = get_loc(gamestate)
            local_print("You look around.")
            lookmap = {}
            for direction in c.DIRECTIONS_AROUND_AND_HERE:
                lookmap[direction] = c.MAP_MAJOR_FEATURE_METADATA[c.MAP_MAJOR_FEATURE.NONE]['symbol']
                look_x, look_y = decomp_coord(c.DIR_OFFSETS[direction])
                new_x, new_y = x + look_x, y + look_y
                if gamestate.can_explore(new_x, new_y):
                    gamestate.explore_coord(new_x, new_y)
                    tile = gamestate.map.get(new_x, new_y)
                    lookmap[direction] = c.MAP_MAJOR_FEATURE_METADATA[tile.type]['symbol']
            splatable = [lookmap[x] for x in c.DIRECTIONS_GRID_AROUND_AND_HERE]
            local_print("{}{}{}\n{}{}{}\n{}{}{}".format(*splatable))
            cmd_look(*args, **kwargs)
        elif arg0 == "list":
            x, y = get_loc(gamestate)
            cmd_look(**kwargs)
            interest_list = []
            for direction in c.DIRECTIONS_AROUND:
                look_x, look_y = decomp_coord(c.DIR_OFFSETS[direction])
                new_x, new_y = x + look_x, y + look_y
                if gamestate.can_explore(new_x, new_y):
                    gamestate.explore_coord(new_x, new_y)
                    tile = gamestate.map.get(new_x, new_y)
                    if tile.type is not c.MAP_MAJOR_FEATURE.NONE:
                        interest_list.append("To the {} you see a {}.".format(c.DIR_DESCRIPTION[direction], tile.name))
            if len(interest_list) > 0:
                local_print("\n".join(interest_list))
            else:
                local_print("There's nothing else of interest around.")
        else:
            local_print("Incorrect direction. Choose from {}.".format(" ".join(c.DIRECTIONS_AROUND)))
            return


def cmd_move(cmd="move", *args, **kwargs):
    if len(args) == 0:
        print("You dance a jig.")
        return

    if not len(args) in [1, 2]:
        print("Incorrect number of arguments for command: {}.".format(cmd))
        return

    # Get the arguments
    direction = c.DIR_NONE
    distance = 1
    if len(args) >= 1:
        direction = args[0]
    if len(args) >= 2:
        distance = args[1]

    if not will_it_int(distance) and not will_it_int(direction):
        print("Unable to understand input.")
        return
    elif will_it_int(distance) and not will_it_int(direction):
        distance = int(distance)
    elif not will_it_int(distance) and will_it_int(direction):
        tmp = distance
        distance = int(direction)
        direction = tmp
    else:
        print("Unable to understand input.")
        return

    if direction not in c.DIRECTIONS_AROUND:
        print("Incorrect direction. Choose from {}.".format(" ".join(c.DIRECTIONS_AROUND)))
        return

    gamestate = get_gamestate(kwargs)
    start_x, start_y = get_loc(gamestate)
    move_x, move_y = decomp_coord(c.DIR_OFFSETS[direction])

    moved = 0
    for step in range(distance):
        start_x += move_x
        start_y += move_y
        if not gamestate.can_explore(start_x, start_y):
            break
        gamestate.explore_coord(start_x, start_y)
        gamestate.current_loc = comp_coord(start_x, start_y)
        if kwargs.get('explore', False):
            cmd_look("look", "around", no_print=True, **kwargs)
        moved += 1

    if moved != distance:
        print("That way is out of bounds.")
    print("You move {} {} time{}.".format(c.DIR_DESCRIPTION[direction], moved, "" if moved == 1 else "s"))


def cmd_math(cmd="math", *args, **kwargs):
    if not len(args) >= 2:
        print('Invalid number of arguments ({}) for command: "{}". Expected at least 2.'.format(len(args), cmd))
    else:
        floatable = True
        for arg in args:
            if not will_it_float(arg):
                floatable = False

        if floatable:
            floats = [float(x) for x in args]

            result = floats[0]
            for x in floats[1:]:
                if cmd == 'add':
                    result += x
                elif cmd == 'sub':
                    result -= x
                elif cmd == 'mul':
                    result *= x
                else:
                    assert cmd == 'div'
                    result /= x

            print("The result is: {}".format(result))
        else:
            print('Invalid arguments ({}) for command: "{}". Expected numbers.'.format(" ".join(args), cmd))


def cmd_help(cmd="help", *args, **kwargs):
    desc_str = ['Available commands ("q" to quit):']
    for cmd in help_cmd_order:
        desc_str.append("    " + "\n    ".join(cmds[cmd].get('desc', [cmd])))
    print("\n".join(desc_str))


def cmd_debug(cmd="debug", *args, **kwargs):
    debugs = ['area']
    if len(args) == 0:
        print("Available debugs: {}".format(debugs))

    if 'area' in args:
        gamestate = get_gamestate(kwargs)
        gamestate.current_area._print_area()


cmds = {
    'map': {'cmd_func': cmd_map, 'desc':        ["map                 - Display a map of the explored area."]},
    'look': {'cmd_func': cmd_look, 'desc':      ["look                - Look at where you are.",
                                                 "look <dir>          - Look in a direction.",
                                                 "look around         - Look around.",
                                                 "look list           - List interesting things nearby."]},
    'move': {'cmd_func': cmd_move, 'desc':      ["move <dir>          - Move in a direction.",
                                                 "move <dir> <n>      - Move n units in dir direction."]},
    'explore': {'cmd_func': cmd_move, 'desc':   ["explore <dir> [<n>] - Look around at destination."], 'kwargs': {'explore': True}},
    'dance': {'cmd_func': cmd_move, 'desc':     ["dance               - WIP"], 'kwargs': {'dancing': True}},
    'add': {'cmd_func': cmd_math},
    'sub': {'cmd_func': cmd_math},
    'mul': {'cmd_func': cmd_math},
    'div': {'cmd_func': cmd_math},
    'help': {'cmd_func': cmd_help, 'desc':      ["help                - Display this help."]},
    'debug': {'cmd_func': cmd_debug}
}
if not c.DEBUG:
    cmds.pop('debug')

help_cmd_order = [
    'map',
    'look',
    'move',
    'explore',
    'dance',
    'add',
    'sub',
    'mul',
    'div',
    'help',
    'debug',
]
