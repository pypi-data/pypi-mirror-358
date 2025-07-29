# -*- coding: utf-8 -*-
from tfcat.codec import dump, dumps, load, loads, TFCatEncoder
from tfcat.utils import coords, split_coords #, map_coords
from tfcat.geometry import Point, LineString, Polygon
from tfcat.geometry import MultiLineString, MultiPoint, MultiPolygon
from tfcat.geometry import GeometryCollection
from tfcat.feature import Feature, FeatureCollection
from tfcat.observation import Observation, ObservationCollection
from tfcat.base import Base
from tfcat.crs import CRS
from tfcat.tfcat import TFCat

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)
__version_info__ = tuple(map(int, __version__.split(".")))
__all__ = (
        [dump, dumps, load, loads, TFCatEncoder] +
        [coords, split_coords] + # map_coords] +
        [Point, LineString, Polygon] +
        [MultiLineString, MultiPoint, MultiPolygon] +
        [GeometryCollection] +
        [Feature, FeatureCollection] +
        [Observation, ObservationCollection] +
        [Base] +
        [CRS] +
        [TFCat] +
        [__version__, __version_info__])
