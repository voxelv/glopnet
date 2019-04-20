from glopnet_lib.utl import ConstEnumerator

DEBUG = True

EXIT_ALIASES = ["stop", "exit", "quit", "q"]

DIR_NONE = '_'
DIR_E = 'e'
DIR_N = 'n'
DIR_W = 'w'
DIR_S = 's'
DIR_NE = 'ne'
DIR_NW = 'nw'
DIR_SW = 'sw'
DIR_SE = 'se'

DIRECTIONS_AROUND = (DIR_E, DIR_N, DIR_W, DIR_S, DIR_NE, DIR_NW, DIR_SW, DIR_SE)
DIRECTIONS_AROUND_AND_HERE = (DIR_NONE, DIR_E, DIR_N, DIR_W, DIR_S, DIR_NE, DIR_NW, DIR_SW, DIR_SE)
DIRECTIONS_GRID_AROUND_AND_HERE = (DIR_NW, DIR_N, DIR_NE, DIR_W, DIR_NONE, DIR_E, DIR_SW, DIR_S, DIR_SE)
DIRECTIONS_CARDINAL = (DIR_E, DIR_N, DIR_W, DIR_S)
DIRECTIONS_CARDINAL_AND_HERE = (DIR_NONE, DIR_E, DIR_N, DIR_W, DIR_S)

DIR_OFFSETS = {
    DIR_NONE: (0, 0),
    DIR_E: (1, 0),
    DIR_N: (0, 1),
    DIR_W: (-1, 0),
    DIR_S: (0, -1),
    DIR_NE: (1, 1),
    DIR_NW: (-1, 1),
    DIR_SW: (-1, -1),
    DIR_SE: (1, -1),
}

DIR_DESCRIPTION = {
    DIR_NONE: "here",
    DIR_E: "East",
    DIR_N: "North",
    DIR_W: "West",
    DIR_S: "South",
    DIR_NE: "Northeast",
    DIR_NW: "Northwest",
    DIR_SW: "Southwest",
    DIR_SE: "Southeast",
}

GAMESTATE = 'gamestate'

# Map Information

TILES_PER_AREA_SIDE = 256
TILES_PER_AREA = TILES_PER_AREA_SIDE * TILES_PER_AREA_SIDE

# TODO: This will get removed when 'real' road-gen is a thing
MIN_ROAD_SPACING = 3


class _tile_enumerator(ConstEnumerator):
    NONE = None
    BARREN_LAND = None
    FACTORY = None
    PRESSURE_TANK = None
    ROAD = None
    PUMP_STATION = None
    PIPELINE = None
    ELECTRICAL_SUBSTATION = None
    SUPPLY_DEPOT = None
    CONTROL_STATION = None
    BRIDGE = None
    POWER_POLE = None
    CHEMICAL_VAT = None
    CONCRETE_DITCH = None


MAP_MAJOR_FEATURE = _tile_enumerator()

_m = MAP_MAJOR_FEATURE
MAP_MAJOR_FEATURE_METADATA = {
    _m.NONE: {'symbol': "."},
    _m.BARREN_LAND: {'symbol': "-"},
    _m.FACTORY: {'symbol': "%"},
    _m.PRESSURE_TANK: {'symbol': "Q"},
    _m.ROAD: {'symbol': "+"},
    _m.PUMP_STATION: {'symbol': "&"},
    _m.PIPELINE: {'symbol': "|"},
    _m.ELECTRICAL_SUBSTATION: {'symbol': "#"},
    _m.SUPPLY_DEPOT: {'symbol': "D"},
    _m.CONTROL_STATION: {'symbol': "["},
    _m.BRIDGE: {'symbol': "^"},
    _m.POWER_POLE: {'symbol': "I"},
    _m.CHEMICAL_VAT: {'symbol': "U"},
    _m.CONCRETE_DITCH: {'symbol': "v"},
}
for feature, metadata in MAP_MAJOR_FEATURE_METADATA.iteritems():
    metadata['name'] = _m.name_of(feature)
