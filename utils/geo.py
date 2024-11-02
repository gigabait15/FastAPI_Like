from utils.utils_import.geo_import import *


async def get_geo(location: str) -> dict:
    """
    Асинхронная функция для получения координат широты и долготы по заданному адресу.
    :param location: адрес в виде строки
    :return: возвращает словарь с широтой и долготой
    """
    async with httpx.AsyncClient() as client:
        # Выполняем асинхронный запрос к Nominatim
        response = await client.get("https://nominatim.openstreetmap.org/search", params={
            'q': location,
            'format': 'json'
        })
        response.raise_for_status()  # Проверка на ошибки

        locations = response.json()

        if not locations:
            return {'latitude': None, 'longitude': None}

        # Извлекаем координаты
        point = Point(float(locations[0]['lon']), float(locations[0]['lat']))

        return {'latitude': point.y, 'longitude': point.x}


async def great_circle_distance(latlong_a: Union[list, tuple] , latlong_b: Union[list, tuple]) -> float|int:
    """
    Асинхронная функция для вычисления расстояния по великой окружности между двумя точками на Земле.
    :param latlong_a: Кортеж или список с широтой и долготой первой точки (lat1, lon1)
    :param latlong_b: Кортеж или список с широтой и долготой второй точки (lat2, lon2)
    :return: Расстояние между точками в метрах
    """
    lat1, lon1 = latlong_a
    lat2, lon2 = latlong_b

    # Разница в радианах между широтами и долготами
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    # Формула haversine для расчета
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Итоговое расстояние с учетом окружности Земли
    d = EARTH_CIRCUMFERENCE * c
    return d
