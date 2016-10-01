import functools

MAX_DISTANCE_INT = 999999


class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated). Taken from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.__doc__ = func.__doc__
        self.__repr__ = func.__repr__

    def __call__(self, *args):
        # if not isinstance(args, collections.Hashable):
        #     # uncacheable. a list, for instance.
        #     # better to not cache than blow up.
        #     return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        f = functools.partial(self.__call__, obj)
        f.__doc__ = self.func.__doc__
        f.__repr__ = self.func.__repr__
        return f

# Below functions are memoized because they are often called many times in large loops

@memoized
def add_points(p1, p2):
    """
    Adds two points together

    :param (int,int) p1: First point
    :param (int,int) p2: Second point
    :return: (p1.x + p2.x, p1.y + p2.y)
    :rtype: (int,int)
    """
    return tuple(map(lambda x, y: x + y, p1, p2))


@memoized
def sub_points(p1, p2):
    """
        Subtracts p2 from p1

        :param (int,int) p1: First point
        :param (int,int) p2: Second point
        :return: (p1.x - p2.x, p1.y - p2.y)
        :rtype: (int,int)
        """
    return tuple(map(lambda x, y: x - y, p1, p2))


@memoized
def scale_point(point, scalar):
    """
    Multiplies the members of the given point by the given scalar

    :param (int,int) point: The point to scale
    :param int scalar: The scalar to multiply by
    :return: (point.x * scalar, point.y * scalar)
    :rtype: (int,int)
    """
    return tuple(map(lambda x: x * scalar, point))


@memoized
def get_point_sign(point):
    """
    Returns the sign of the given point's members

    :param (int,int)  The point to operate on
    :return: (sign(point.x), sign(point.y)) where sign of n < 0 => -1, n == 0 => 0, n > 0 => 1
    :rtype: (int,int)
    """
    return tuple(map(lambda x: -1 if x < 0 else (1 if x > 0 else 0), point))


@memoized
def are_points_inline(p1, p2):
    """
    Checks whether two points are in a line with each other. That is, can one point be reached from the other
    by only travelling in one of the 8 cardinal directions.

    :param (int,int) p1: First point
    :param (int,int) p2: Second point
    :return: True if the points are inline, False otherwise
    :rtype: bool
    """
    delta = sub_points(p1, p2)
    return delta[0] == 0 or delta[1] == 0 or abs(delta[0]) == abs(delta[1])

@memoized
def chebyshev_distance(point_1, point_2):
    """
    Returns the Chebyshev (or chessboard) distance between the two given points.

    This is also the minimum number of moves that must be made to reach
    point b from point a or vice versa, assuming there are no obstacles in the way.

    :param (int,int) point_1: The starting point
    :param (int,int) point_2: The destination point
    :rtype: int
    """
    return max(abs(point_1[0] - point_2[0]), abs(point_1[1] - point_2[1]))

