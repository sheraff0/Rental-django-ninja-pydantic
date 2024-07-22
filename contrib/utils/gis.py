import re
from django.contrib.gis.geos import Point


def coords_to_list(value):
    try:
        return [*map(float, re.findall("\d+\.\d+", str(value))[::-1])]
    except:
        return ""


def list_to_coords(values):
    try:
        return Point(*map(float, values[::-1]), srid=4326)
    except:
        return Point(30.307216, 59.944259, srid=4326)
