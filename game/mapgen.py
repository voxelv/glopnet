import const as c
from glopnet_lib.utl import *


class Area(object):

    grid = [c.MAP_MAJOR_FEATURE.NONE] * c.TILES_PER_AREA

    @staticmethod
    def _index_2d_to_1d(x, y):
        return (y * c.TILES_PER_AREA_SIDE) + x

    def __init__(self):
        self._generate_roads()

    def get(self, x, y):
        return self.grid[self._index_2d_to_1d(x, y)]

    def _generate_roads(self):
        num_vpoints_start = c.TILES_PER_AREA_SIDE / 4
        num_vpoints_var = int(num_vpoints_start * .05)
        num_vpoints = rand_int_var(num_vpoints_start, num_vpoints_var)

        first_cross_point = (rand_int(c.TILES_PER_AREA_SIDE), rand_int(c.TILES_PER_AREA_SIDE))

        gens = [
            # {'oline': (first_cross_point[0], 0, first_cross_point[0], c.TILES_PER_AREA_SIDE - 1)},
            # {'oline': (0, first_cross_point[1], c.TILES_PER_AREA_SIDE - 1, first_cross_point[1])},
            {'cross': first_cross_point, 'type': c.MAP_MAJOR_FEATURE.ROAD}
        ]
        for gen_i in xrange(num_vpoints):
            x = rand_int(c.TILES_PER_AREA_SIDE)
            y = rand_int(c.TILES_PER_AREA_SIDE)

            gens.append({'cross': (x, y), 'type': c.MAP_MAJOR_FEATURE.ROAD})

        self._write_gens(gens)

    def _write_gens(self, gens):
        # Do 'cross' gens
        cross_gens = []
        for gen in [g for g in gens if 'cross' in g]:  # Go through all the cross gens in gens
            allow = True
            for cg in cross_gens:
                genx, geny = gen['cross']
                cgx, cgy = cg['cross']
                if not(abs(genx - cgx) > c.MIN_ROAD_SPACING and abs(geny - cgy) > c.MIN_ROAD_SPACING):
                    allow = False
            if allow:
                cross_gens.append(gen)

        for gen in cross_gens:
            x, y = gen['cross']
            for i in xrange(c.TILES_PER_AREA_SIDE):
                self.grid[self._index_2d_to_1d(x, i)] = gen['type']
                self.grid[self._index_2d_to_1d(i, y)] = gen['type']

    def _print_area(self):
        out_str = ""
        for y in xrange(c.TILES_PER_AREA_SIDE):
            for x in xrange(c.TILES_PER_AREA_SIDE):
                tile_type = self.get(x, y)
                out_str += c.MAP_MAJOR_FEATURE_METADATA[tile_type]['symbol']
            out_str += "\n"
        print out_str


if __name__ == '__main__':
    a = Area()
    a._print_area()



