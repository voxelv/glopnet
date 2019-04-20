class ContinuousGrid(object):
    """ContinuousGrid
    Implements an expandable grid using a dictionary
    """

    def __init__(self, default=None):
        super(ContinuousGrid, self)
        self.items = {}
        self.default = default
        self.width = 0
        self.height = 0
        self.low_left_coord = (0, 0)

    def _filter_coords(self, x, y):
        """
        Filters any input coordinates to ensure they are integers.
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :returns: The tuple of valid (x, y)
        :rtype: (int, int)
        """
        if not isinstance(x, int):
            raise TypeError("x coord is not an integer!")
        if not isinstance(y, int):
            raise TypeError("y coord is not an integer!")
        return x, y

    def _recalc_w_h(self):
        """
        Recalculates the width and height of the grid based on the bottom-left-most entry, and top-right-most entry
        """
        def _one_pass_min_max(iterable):
            min_val = iterable[0]
            max_val = iterable[0]
            for item in iterable:
                min_val = min(item, min_val)
                max_val = max(item, max_val)
            return min_val, max_val

        self.width = 0
        self.height = 0
        xcoords = [coord[0] for coord in self.items.keys()]
        ycoords = [coord[1] for coord in self.items.keys()]
        if len(xcoords) > 0 and len(ycoords) > 0:
            minx, maxx = _one_pass_min_max(xcoords)
            self.width = maxx - minx + 1
            miny, maxy = _one_pass_min_max(ycoords)
            self.height = maxy - miny + 1
            self.low_left_coord = (minx, miny)

    def coord_in_grid(self, x, y):
        """
        Returns whether a coordinate is in the grid
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :return: Whether the coordinate is in the grid
        :rtype: bool
        """
        return (x, y) in self.items

    def set(self, x, y, obj):
        """
        Sets the object at the position (x, y). Overwrites any previously set object.
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :param obj: The object
        :type obj: object
        """
        x, y = self._filter_coords(x, y)
        self.items[(x, y)] = obj
        self._recalc_w_h()

    def get(self, x, y):
        """
        Gets the object at position (x, y). Does not remove it.
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :returns: The object at (x, y)
        :rtype: object
        """
        x, y = self._filter_coords(x, y)
        return self.items.get((x, y), self.default)

    def pop(self, x, y):
        """
        Gets and removes the object at position (x, y).
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :returns: The object that was at (x, y)
        :rtype: object
        """
        x, y = self._filter_coords(x, y)
        ret_obj = self.items.pop((x, y), self.default)

        self._recalc_w_h()

        return ret_obj

    def __str__(self):
        """
        Displays the grid line by line using string representations of the objects in the grid.
        :returns: The string to display the grid
        :rtype: str
        """
        ret_str = ""
        if len(self.items.keys()) == 0:
            ret_str = ""
        elif len(self.items.keys()) == 1:
            ret_str = "{}\n".format(str(self.items.values()[0]))
        else:
            for y in reversed(range(self.height)):
                y += self.low_left_coord[1]
                for x in range(self.width):
                    x += self.low_left_coord[0]
                    ret_str += str(self.items.get((x, y), self.default))
                ret_str += "\n"

        return ret_str
