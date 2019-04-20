from continuous_grid import ContinuousGrid
import const as c
from mapgen import Area
from glopnet_lib.utl import coord_is_valid, rand_int


class GlopnetGamestate(object):

    map = ContinuousGrid(default=" ")
    current_loc = (int(c.TILES_PER_AREA_SIDE / 2), int(c.TILES_PER_AREA_SIDE / 2))
    current_area = Area()

    def __init__(self):
        super(GlopnetGamestate, self).__init__()
        self._valid = True

        for d in c.DIRECTIONS_CARDINAL_AND_HERE:
            x = self.current_loc[0] + c.DIR_OFFSETS[d][0]
            y = self.current_loc[1] + c.DIR_OFFSETS[d][1]
            self.explore_coord(x, y)

    def is_valid(self):
        return self._valid

    def can_explore(self, x, y):
        return 0 <= x < c.TILES_PER_AREA_SIDE and 0 <= y < c.TILES_PER_AREA_SIDE

    def explore_coord(self, x, y):
        if not coord_is_valid((x, y)):
            print "Coord is not valid."
            return

        if not self.map.coord_in_grid(x, y):
            tile = self.gen_new_tile2(x, y)
            # tile = self.gen_new_tile1()
            self.map.set(x, y, tile)

    def gen_new_tile2(self, x, y):
        tile_type = self.current_area.get(x, y)
        m = c.MAP_MAJOR_FEATURE_METADATA
        return Tile(tile_type, m[tile_type]['symbol'], m[tile_type]['name'])

    def gen_new_tile1(self):
        tile_types = [
            {'type': 0, 'symbol': "-", 'name': "Barren Land"},
            {'type': 1, 'symbol': "F", 'name': "Factory"},
            {'type': 2, 'symbol': "T", 'name': "Large Storage Tank"},
            {'type': 3, 'symbol': "R", 'name': "Road"},
            {'type': 4, 'symbol': "P", 'name': "Pumping Station"},
            {'type': 5, 'symbol': "L", 'name': "Pipeline"},
            {'type': 6, 'symbol': "E", 'name': "Electrical Substation"},
            {'type': 7, 'symbol': "D", 'name': "Supply Depot"},
        ]
        tile_info = tile_types[rand_int(len(tile_types))]
        return Tile(tile_info['type'], tile_info['symbol'], tile_info['name'])


class Tile(object):
    x = None
    y = None

    def __init__(self, typ, symbol, name, **kwargs):
        super(Tile, self).__init__()
        self.type = typ
        self.symbol = symbol
        self.name = name
        self.attributes = kwargs

    def __str__(self):
        return self.symbol
