"""
Author: Big Panda
Created Time: 26.06.2025 11:48
Modified Time: 26.06.2025 11:48
Description:
    使用与 np.array() 类似的惯例来定义 ArrayPoint2D 函数，参数 object 应该为 list 对象
"""
from __future__ import annotations
from Points2D import *
from typing import Tuple

__all__ = ['ArrayPoint2D']


class ArrayPoint2D(list):
    def __init__(self: ArrayPoint2D, obj) -> None:
        if all([isinstance(item, Point2D) for item in obj]):
            super().__init__(obj)
        else:
            raise ValueError("The input value is not an ArrayPoint2D.")

    # String representation of ArrayPoint2D
    # Override __str__() method in parent list
    def __str__(self: ArrayPoint2D) -> str:
        """
        Express ArrayPoint2D
        """
        return f"ArrayPoint2D{super().__str__()}"

    def sort(self, *, key=None, reverse=False):
        if not reverse:
            super().sort(key=lambda p: (p[0], p[1]))
        else:
            super().sort(key=lambda p: (-p[0], -p[1]))

    def appends(self, other: Point2D | Tuple[Point2D]):
        if isinstance(other, Point2D):
            super().append(other)
        elif isinstance(other, tuple) and all(isinstance(item, Point2D) for item in other):
            super().extend(other)
        else:
            raise ValueError("The input value of append function should be Point2D or Tuple[Point2D]")


if __name__ == '__main__':
    p1 = Point2D(1, 2)
    p2 = Point2D(4, 6)
    test = ArrayPoint2D([p1, p2])
    print(test)

    # sort() 方法
    p1 = Point2D(1, 2)
    p2 = Point2D(4, 6)
    p3 = Point2D(2, 2)
    p4 = Point2D(2, 6)
    test = ArrayPoint2D([p1, p2, p3, p4])
    test.sort()
    print(test)
