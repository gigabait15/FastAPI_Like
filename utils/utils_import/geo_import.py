import httpx
from shapely.geometry import Point
import math
from typing import Union


EARTH_CIRCUMFERENCE = 6378137  # окружность Земли в метрах [1](https://gist.github.com/gabesmed/1826175)