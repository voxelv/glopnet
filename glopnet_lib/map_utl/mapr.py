from glopnet_lib import drandom
from glopnet_lib.utl import DIR


class Coord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({})".format(self.__repr__())

    def __repr__(self):
        return "{},{}".format(self.x, self.y)

    def __eq__(self, other):
        result = self.__repr__() == other.__repr__()
        return result

    def __ne__(self, other):
        result = self.__repr__() != other.__repr__()
        return result

    def set(self, coord):
        self.x = coord.x
        self.y = coord.y
        return self


class GeneratedAreaItem:
    default_char = "-"

    def __init__(self, **kwargs):
        self.info = {'char': self.default_char}
        if kwargs is not None and isinstance(kwargs, dict):
            self.set_info(**kwargs)

    def __repr__(self):
        return self.get_printable_char()

    def __eq__(self, other):
        result = self.__repr__() == other.__repr__()
        return result

    def __ne__(self, other):
        result = self.__repr__() != other.__repr__()
        return result

    def get_printable_char(self):
        return self.info['char']

    def set_info(self, **kwargs):
        self.info.update(kwargs)


class GeneratedArea:

    # ------------------------------------------------------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, side=None, width=None, height=None):
        self.valid = False
        self._items = None

        if side is not None:
            self._height = side
            self._width = side
        elif height is not None and width is not None:
            self._height = height
            self._width = width

        if side is not None or (height is not None and width is not None):
            self._items = self._get_memory()
            self.valid = True

    # ------------------------------------------------------------------------------------------------------------------
    # Internal overrides
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self._generated_area_str()

    def __copy__(self):
        result = self._get_memory()
        for i in xrange(len(result)):
            result[i].set_info(**self._items[i].info)
        return result

    # ------------------------------------------------------------------------------------------------------------------
    # Static methods
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _xy_to_idx(x, y, width):
        result = (y * width) + x
        return result

    @staticmethod
    def _is_coord(coord):
        result = isinstance(coord, Coord)
        if not result:
            print("Error. {} is not a 'Coord'.".format(type(coord).__name__))
        return result

    # ------------------------------------------------------------------------------------------------------------------
    # Private functions
    # ------------------------------------------------------------------------------------------------------------------

    def _get_memory(self):
        # items = [GeneratedAreaItem()] * (self._height * self._width)
        items = []
        for i in xrange(self._width):
            for j in xrange(self._height):
                items.append(GeneratedAreaItem())
        return items

    def _coord_in_area(self, coord):
        result = True
        result &= coord.x >= 0
        result &= coord.y >= 0
        result &= coord.x < self._width
        result &= coord.y < self._height
        return result

    def _check_coord_is_valid(self, coord):
        result = True
        result &= self._is_coord(coord)
        result &= self._coord_in_area(coord)
        return result

    def _coord_to_idx(self, coord, width):
        result = self._xy_to_idx(coord.x, coord.y, width)
        return result

    def _get_at(self, coord):
        result = self._items[self._coord_to_idx(coord, self._width)]
        return result

    def _set_at(self, coord, item):
        self._items[self._coord_to_idx(coord, self._width)] = item

    def _generated_area_str(self):
        result = ""
        if self.valid:
            for i in xrange(self._height):
                row = ""
                for j in xrange(self._width):
                    row += self._items[self._xy_to_idx(j, i, self._width)].get_printable_char()
                result += row + '\n'
        return result

    # ------------------------------------------------------------------------------------------------------------------
    # Public functions
    # ------------------------------------------------------------------------------------------------------------------

    def set(self, coord, item):
        successful = False
        if self.valid and self._check_coord_is_valid(coord):
            x = self._get_at(coord)
            self._set_at(coord, item)
            del x
            successful = True
        return successful

    def get(self, coord):
        if self.valid and self._check_coord_is_valid(coord):
            return self._get_at(coord)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_items(self):
        result = None
        if self.valid:
            result = self.__copy__()
        return result


class GeneratedAreaGenerator:
    def __init__(self, item, start_coord):
        if GeneratedArea._is_coord(start_coord):
            self.gen_area_item = item
            self.start_coord = start_coord

    def _check_valid(self, gen_area):
        valid = True
        if not isinstance(gen_area, GeneratedArea):
            print "Error. {} is not a 'GeneratedArea'.".format(type(gen_area).__name__)
            valid = False
        if not isinstance(self.gen_area_item, GeneratedAreaItem):
            print "Error. {} is not a 'GeneratedAreaItem'.".format(type(self.gen_area_item).__name__)
            valid = False
        return valid

    def generate(self, gen_area):
        """
        :param gen_area: The GeneratedArea object to generate on
        :type gen_area: GeneratedArea
        """
        self._check_valid(gen_area)
        pass


class GeneratedAreaBoxGenerator(object, GeneratedAreaGenerator):
    def __init__(self, item, start_coord, width, height, filled=True):
        GeneratedAreaGenerator.__init__(self, item, start_coord)
        self.width = width
        self.height = height
        self.filled = filled

    def set_item(self, gen_area_item):
        self.gen_area_item = gen_area_item
        return self

    def set_filled(self, filled):
        self.filled = filled
        return self

    def _generate_filled(self, gen_area):
        coord = Coord().set(self.start_coord)
        for i in xrange(self.width):
            for j in xrange(self.height):
                coord.x = self.start_coord.x + i
                coord.y = self.start_coord.y + j
                gen_area.set(coord, GeneratedAreaItem(**self.gen_area_item.info))

    def _generate_outline(self, gen_area):
        coord = Coord().set(self.start_coord)
        for i in xrange(self.width):
            coord.x = self.start_coord.x + i
            coord.y = self.start_coord.y
            gen_area.set(coord, GeneratedAreaItem(**self.gen_area_item.info))
            coord.y = self.start_coord.y + self.height - 1
            gen_area.set(coord, GeneratedAreaItem(**self.gen_area_item.info))
        for j in xrange(self.height):
            coord.x = self.start_coord.x
            coord.y = self.start_coord.y + j
            gen_area.set(coord, GeneratedAreaItem(**self.gen_area_item.info))
            coord.x = self.start_coord.x + self.width - 1
            gen_area.set(coord, GeneratedAreaItem(**self.gen_area_item.info))

    def generate(self, gen_area):
        if self._check_valid(gen_area):
            if self.filled:
                self._generate_filled(gen_area)
            else:
                self._generate_outline(gen_area)


class GeneratedAreaLineProbeGenerator(object, GeneratedAreaGenerator):
    def __init__(self, item, start_coord, direction=DIR.N, probe_stop_pct=10):
        GeneratedAreaGenerator.__init__(self, item, start_coord)
        self.direction = direction
        self.probe_stop_pct = probe_stop_pct

    def generate(self, gen_area):
        if self._check_valid(gen_area):
            write_coord = self.start_coord
            while gen_area._coord_in_area(write_coord):
                # Check current location
                item_at_wc = gen_area.get(write_coord)
                default_item = GeneratedAreaItem()

                # If not default, check if we keep going (randomly)
                if item_at_wc != default_item:
                    if drandom(100) < self.probe_stop_pct:
                        break

                # If we got here, set the current location
                gen_area.set(write_coord, self.gen_area_item)

                # Increment the current location
                ofst = DIR.get_ofst(self.direction)
                write_coord.x += ofst[0]
                write_coord.y += ofst[1]

