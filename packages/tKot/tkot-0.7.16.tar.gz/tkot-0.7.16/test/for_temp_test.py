import numpy as np
from typing import Self
from numpy.typing import NDArray
from src.tKot.common import Size, Point, SmoothBox
import timeit

# Ваши классы Coords, Point, Size, Polygon и SmoothBox здесь...

# Тестируем создание SmoothBox.from_size
def test_from_size():
    size = Size(100, 100)
    base = Point(0, 0)
    return SmoothBox.from_size(size, base)

# Тестируем создание SmoothBox.from_size и затем сложение с Point
def test_from_size_plus_point():
    size = Size(100, 100)
    base = Point(0, 0)
    box = SmoothBox.from_size(size, base)
    return box + Point(1, 1)

# Количество повторений для теста
n = 10000

# Измеряем время создания
create_time = timeit.timeit(test_from_size, number=n)
print(f"SmoothBox.from_size: {create_time/n:.7f} секунд на операцию")

# Измеряем время создания и сложения
create_plus_time = timeit.timeit(test_from_size_plus_point, number=n)
print(f"SmoothBox.from_size + Point: {create_plus_time/n:.7f} секунд на операцию")
print(f"Разница: {(create_plus_time - create_time)/n:.7f} секунд")