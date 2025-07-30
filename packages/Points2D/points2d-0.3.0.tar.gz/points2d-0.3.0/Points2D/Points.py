"""
Author: Big Panda
Time: 13.06.2024 17:03
Description:
    Class for creating a 2d point
"""
from __future__ import annotations
import numpy as np
import random

__all__ = ['Point2D',
           "LinkPoint2D"]


class Point2D:
    _x: int | float = 0
    _y: int | float = 0
    _doc: str

    def __init__(self: Point2D, *args) -> None:
        """
        Define two methods for initializing Point2D
            1. point = Points2D((x, y))
            2. point = Points2D([x, y])
            3. point = Points2D({'x' : x, 'y' : y})
            4. point = Points2D(x, y)
            5. point = Points2D(Points2D(x, y), (offset_x, offset_y))
            6. point = Points2D(Points2D(x, y), [offset_x, offset_y])
        """
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, (tuple, list)) and len(arg) == 2:
                self.x, self.y = arg
            elif isinstance(arg, dict):
                self.x = arg.get('x', 0.0)
                self.y = arg.get('y', 0.0)
            else:
                raise ValueError("""\nThe input one arguments must be:
    Point2D(Tuple(num1 : int | float, num2 : int | float))
    Point2D(List[num1 : int | float, num2 : int | float])
    Point2D(Dict({"x" : int | float, "y" : int | float}))""")
        elif len(args) == 2:
            if isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                self.x, self.y = args
            elif isinstance(args[0], Point2D) and isinstance(args[1], (tuple, list)) and len(args[1]) == 2:
                self.x, self.y = args[0].x + args[1][0], args[0].y + args[1][1]
            else:
                raise ValueError("""\nThe input two arguments must be:
    Point2D(num1 : int | float, num2 : int | float)        
    Point2D(Point2D, Tuple(num1 : int | float))        
    Point2D(Point2D, List[num2 : int | float])""")
        else:
            raise ValueError('The number of input arguments should only be 0, 1, 2.')

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("x is not a rational number")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("y is not a rational number")
        self._y = value

    # String representation of Point2D
    def __str__(self: Point2D) -> str:
        # return f"Point2D{self.x, self.y}" 书可以写一下关于这里的
        return f"Point2D({self.x}, {self.y})"

    def __repr__(self: Point2D) -> str:
        return f"Point2D({self.x}, {self.y})"

    # Override setitem method
    def __setitem__(self: Point2D, key: int, value: int | float) -> None:
        if key == 0:
            self.x: int | float = value
        elif key == 1:
            self.y: int | float = value
        else:
            raise ValueError('The index of Point2D object is out of range.')

    # Override getitem method
    def __getitem__(self: Point2D, key: int) -> float:
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise ValueError('The index of Point2D object is out of range.')

    def __iter__(self: Point2D) -> iter(Point2D):
        return iter([self.x, self.y])

    def __copy__(self: Point2D) -> Point2D:
        return Point2D(self.x, self.y)

    def __neg__(self: Point2D) -> Point2D:
        return Point2D(-self.x, -self.y)

    def __abs__(self: Point2D) -> Point2D:
        """
        Get absolute point coordinates of current one. In first Quadrant.
        """
        return Point2D(abs(self.x), abs(self.y))

    def __add__(self: Point2D, other: Point2D) -> Point2D:
        """
        Point2D operation ------ Adding
        """
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self: Point2D, other: Point2D) -> Point2D:
        """
        Point2D operation ------ Subtraction
        """
        return Point2D(self.x - other.x, self.y - other.y)

    # ================================================= Specific function =================================================
    def tolist(self):
        return [self.x, self.y]

    def index(self: Point2D, other: int | float | Point2D) -> int:
        """
        if other is <int> or <float>:
            Return the index of coordinate equals to num
        if other is Point2D:
            Return the index of coordinate of point 1 equals to point 2
        :param other: reference number
        :return: 0 for x, 1 for y, -1 for no suitable coordinate
        """
        if isinstance(other, (int, float)):
            indices = [index for index, value in enumerate(self) if value == other]
        else:
            indices = [index for index, value in enumerate(self - other) if value == 0]
        return indices[0] if indices else -1

    def symmetry_about_x(self: Point2D):
        symmetry_matrix = np.array([[1, 0],
                                    [0, -1]])

        return symmetry_matrix @ self

    def symmetry_about_y(self: Point2D):
        symmetry_matrix = np.array([[-1, 0],
                                    [0, 1]])

        return symmetry_matrix @ self

    def symmetry_about_origin(self: Point2D):
        symmetry_matrix = np.array([[-1, 0],
                                    [0, -1]])

        return symmetry_matrix @ self

    def symmetry_about_y_equal_x(self: Point2D):
        symmetry_matrix = np.array([[0, 1],
                                    [1, 0]])

        return symmetry_matrix @ self

    def symmetry_about_y_equal_minus_x(self: Point2D):
        symmetry_matrix = np.array([[0, -1],
                                    [-1, 0]])

        return symmetry_matrix @ self

    def symmetry_about_x_parallel(self: Point2D, axis: int | float = 0.0):
        """
        Symmetric about y-axis, which y does not equal to zero. Here, the value of axis ！= 0

        Steps:
        1. Subtract 1 from x-coordinates
        2. Switch sign of x-coordinates
        3. Add 1 to x-coordinates
        :param point: the point or vector we deal with, normally a 2d vector
        :param axis: the symmetric axis
        :return: point after symmetry
        """
        translate_matrix_1 = np.array([[1, 0, 0],
                                       [0, 1, -axis],
                                       [0, 0, 1]])
        symmetry_matrix = np.array([[1, 0, 0],
                                    [0, -1, 0],
                                    [0, 0, 1]])
        translate_matrix_2 = np.array([[1, 0, 0],
                                       [0, 1, axis],
                                       [0, 0, 1]])

        point_3d = np.ones((3, 1), dtype=np.float64)
        point_3d[0:-1, 0] = np.array(self.tolist())
        new_point_3d = translate_matrix_2 @ symmetry_matrix @ translate_matrix_1 @ point_3d

        return Point2D(new_point_3d[:-1, 0].tolist())

    def symmetry_about_y_parallel(self: Point2D, axis: int | float = 0.0):
        """
        Symmetric about y-axis, which y does not equal to zero. Here, the value of axis ！= 0
        :param point:
        :param axis:
        :return:
        """
        translate_matrix_1 = np.array([[1, 0, -axis],
                                       [0, 1, 0],
                                       [0, 0, 1]])
        symmetry_matrix = np.array([[-1, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1]])
        translate_matrix_2 = np.array([[1, 0, axis],
                                       [0, 1, 0],
                                       [0, 0, 1]])
        point_3d = np.ones((3, 1), dtype=np.float64)
        point_3d[0:-1, 0] = np.array(self.tolist())
        new_point_3d = translate_matrix_2 @ symmetry_matrix @ translate_matrix_1 @ point_3d
        # print(new_point_3d[:-1, 0])
        # print(Point2D([5., 1.]))
        # print(Point2D(new_point_3d[:-1, 0]))
        # print(type(new_point_3d[:-1, 0]))

        return Point2D(new_point_3d[:-1, 0].tolist())

    def in_region(self, p1, p2):
        """
        Judge whether current point locates in the rectangular region that consists of p1 and p2
        """
        x_min = min(p1[0], p2[0])
        x_max = max(p1[0], p2[0])
        y_min = min(p1[1], p2[1])
        y_max = max(p1[1], p2[1])

        # 判断点的坐标是否在矩形范围内
        return (x_min <= self[0] <= x_max) and (y_min <= self[1] <= y_max)

    def manhattan_connection(self, other: Point2D, choice: int = 1, pg: Point2D = None):
        """
        self: current point
        other: the point connected with the current point
        choice: In default choice = 1, we interpolate one point, because this is the simplest case.
                choice = 2 means we interpolate two points
                choice = 0 means we specify one point and then do interpolation according to this point(maybe contains the original point)
        """
        if choice == 0:
            if pg is None:
                raise ValueError("You should specify the given point.")
            else:
                lst = [(Point2D(pg.x, self.y), Point2D(pg.x, other.y)), (Point2D(self.x, pg.y), Point2D(other.x, pg.y))]
                return lst[random.choice([0, 1])]
        elif choice == 1:
            id_x = random.choice([0, 1])  # Use random to imitate default link strategy
            id_y = 1 - id_x
            return Point2D([self.x, other.x][id_x], [self.y, other.y][id_y])
        elif choice == 2:
            array_x = np.arange(self.x, other.x, 1).tolist()
            x = random.choice(array_x[1:])
            return Point2D(x, self.y), Point2D(x, other.y)


class LinkPoint2D(Point2D):
    _direction: str = "E"

    def __init__(self, *args, direction="E"):
        super().__init__(*args)
        self.direction = direction

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value

    def __str__(self):
        return f"({self.x}, {self.y}, direction={self.direction})"

    def __repr__(self):
        return f"({self.x}, {self.y}, direction={self.direction})"

    def manhattan_connection(self, other: Point2D, choice: int = 1, pg: Point2D = None):
        pass


if __name__ == '__main__':
    # ====== Point creation method 1
    point2d_1 = Point2D(1, 1)
    point2d_2 = Point2D(2, 2)
    print(point2d_1 + point2d_2)
    # ====== Point creation method 2
    point2d_1 = Point2D(1, 1)
    point2d_2 = Point2D(point2d_1, (2, 2))
    print(point2d_2)
    print(point2d_1 + point2d_2)
    # symmetry_about_y_parallel
    point2d_1 = Point2D(1, 1)
    point2d_2 = point2d_1.symmetry_about_y_parallel(3)
    print(point2d_2)
