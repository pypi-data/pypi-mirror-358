"""
This class is adapted from: https://github.com/jazzband/geojson/blob/master/geojson/feature.py
"""


from tfcat.base import Base
from tfcat.crs import DefaultCRS, CRS
from tfcat.validate import JSONSCHEMA_URI
from astropy.table import Table, Column
from tfcat.utils import split_coords
from astropy.time import Time
from shapely.geometry import shape
from matplotlib import pyplot as plt
from typing import Union
import numpy

dtype_mapping = {
    'int': numpy.int32,
    'float': numpy.float32,
    'str': str
}


class Feature(Base):
    """Class for a TFcat feature

    :param id: Feature identifier, such as a sequential number.
    :type id: str, int
    :param geometry: Geometry corresponding to the feature.
    :param properties: Dict containing properties of the feature.
    :type properties: dict
    :return: Feature object
    :rtype: Feature
    """

    def __init__(self, id=None,
                 geometry=None, properties=None, **extra):
        """Initialises a Feature object with the given parameters.
        """
        super(Feature, self).__init__(**extra)
        self["id"] = id
        self["geometry"] = (self.to_instance(geometry, strict=True)
                            if geometry else None)
        self["properties"] = properties or {}

    def errors(self):
        geo = self.get('geometry')
        return geo.errors() if geo else None

    @property
    def tmin(self) -> float:
        """Returns the lower bound of the time axis.

        :return: Lower bound of the time axis
        :rtype: float
        """
        return self.bbox[0]

    @property
    def tmax(self):
        """Returns the upper bound of the time axis.

        :return: Upper bound of the time axis
        :rtype: float
        """
        return self.bbox[2]

    @property
    def fmin(self):
        """Returns the lower bound of the spectral axis.

        :return: Lower bound of the spectral axis
        :rtype: float
        """
        return self.bbox[1]

    @property
    def fmax(self):
        """Returns the upper bound of the spectral axis.

        :return: Upper bound of the spectral axis
        :rtype: float
        """
        return self.bbox[3]

    @property
    def bbox(self):
        """Returns the bounding box.

        The bounding box refers to the smallest rectangle including the geometry, with sides aligned with the
        temporal and spectral axes.

        :return: Bounding box.
        :rtype: Union[list[float], None]
        """
        return shape(self.geometry).bounds if self.geometry else None

    def __len__(self):
        """Length of the collection

        :return: number of collection features.
        :rtype: int
        """
        return len(self.geometry.coordinates) if self.geometry else 0

    def _plot(self, crs=None):
        ftype = self['geometry']['type']
        coord = self['geometry']['coordinates']
        if ftype not in ['MultiLineString', 'MultiPolygon']:
            coord = [coord]

        plot_style = '+-'
        if ftype.endswith('Point'):
            plot_style = '+'

        for item in coord:
            itimes, ifreqs = split_coords(item, crs=crs)
            if crs is not None:
                plt.plot(itimes.datetime, ifreqs.value, plot_style)
            else:
                plt.plot(itimes, ifreqs, plot_style)

    def _plot_bbox(self, crs=None):
        bbox_times = [self.tmin, self.tmax, self.tmax, self.tmin, self.tmin]
        if crs is not None:
            bbox_times = crs.time_converter(bbox_times).datetime
        bbox_freqs = [self.fmin, self.fmin, self.fmax, self.fmax, self.fmin]
        plt.plot(bbox_times, bbox_freqs, '--', label='bbox')

    def plot(self, crs=None):
        """Plots the feature.

        :param crs: Input CRS
        :type crs: CRS
        """
        self._plot(crs)
        self._plot_bbox(crs)

        if crs is not None:
            plt.xlabel(crs.properties['time_coords']['name'])
            plt.ylabel(f"{crs.properties['spectral_coords']['name']} ({crs.properties['spectral_coords']['unit']})")

        plt.title(f"({self['geometry']['type']})")

        plt.show()


class FeatureCollection(Base):
    """Class for a TFcat feature collection.

    A FeatureCollection is a list Feature objects.

    :param features: List of features to constitute the FeatureCollection.
    :type features: iterable
    :param properties: Feature collection global properties
    :type properties: Union[dict, None]
    :param fields: Fields defining the feature properties
    :type fields: Union[list[Field], None]
    :param crs: Coordinate reference system
    :type crs: Union[dict, CRS, None]
    :param schema: TFCat JSON Schema URI (default to the current supported JSON Schema)
    :type schema: str
    :return: FeatureCollection object
    :rtype: FeatureCollection
    """

    def __init__(self, features=None, properties=None, fields=None, crs=None, schema=JSONSCHEMA_URI, **extra):
        """
        Initialises a FeatureCollection object from the
        """
        super(FeatureCollection, self).__init__(**extra)
        self["$schema"] = schema
        self["features"] = features
        self["fields"] = fields or {}
        self["properties"] = properties or {}
        self["crs"] = CRS(crs=crs) or DefaultCRS

    def errors(self):
        return self.check_list_errors(lambda x: x.errors(), self.features)

    def __getitem__(self, key):
        try:
            return self.get("features", ())[key]
        except (KeyError, TypeError, IndexError):
            return super(Base, self).__getitem__(key)

    def __len__(self):
        return len(self.features)

    def as_table(self):
        """Produces an Astropy Table object containing the TFCat data

        :return: table object with the feature collection
        :rtype: Table
        """

        cols = [
            _FeatureColumn(
                name='feature',
                data=[item.geometry for item in self.features],
                description='Feature',
                crs=self.crs,
                properties=self.properties,
                schema=self['$schema'],
            ),
            Column(
                name='tmin',
                data=[self.crs.time_converter(item.bbox[0]).iso for item in self.features],
                description='Feature Start Time',
                meta={"ucd": "time.start"}
            ),
            Column(
                name='tmax',
                data=[self.crs.time_converter(item.bbox[2]).iso for item in self.features],
                description='Feature End Time',
                meta={"ucd": "time.end"}
            ),
            Column(
                name='fmin',
                data=[item.bbox[1] for item in self.features],
                unit=self.crs.properties['spectral_coords']['unit'],
                description='Feature lower spectral bound',
                meta={"ucd": "em.freq;stat.min"}
            ),
            Column(
                name='fmax',
                data=[item.bbox[3] for item in self.features],
                unit=self.crs.properties['spectral_coords']['unit'],
                description='Feature upper spectral bound',
                meta = {"ucd": "em.freq;stat.max"}
            )
        ]

        for key in self.fields:
            cur_col = Column(
                name=key,
                dtype=dtype_mapping[self.fields[key]['datatype']],
                data=[item.properties[key] for item in self.features],
                unit=self.fields[key].get('unit', None),
                description=self.fields[key].get('info', None)
            )
            cur_col.meta = {
                'ucd': self.fields[key].get('ucd', None),
                'datatype': self.fields[key].get('datatype', None),
                'options': self.fields[key].get('values', None),
            }
            cols.append(cur_col)

        return Table(
            cols,
            meta={
                "crs": self.crs,
                "properties": self.properties,
                "schema": self['$schema'],
            }
        )

    @classmethod
    def from_table(cls, table, properties=None, fields=None, crs=None, schema=JSONSCHEMA_URI):
        """Creates a FeatureCollection from an Astropy Table object containing TFCat data.

        The Table input must follow the same structure as the table exported by the as_table()
        method of this class.

        Additional properties can be included in the `properties` and `fields` inputs.

        :param table: Input table
        :type table: Table
        :param properties: table level properties
        :type properties: Union[Dict, None]
        :param fields: property field descriptions
        :type fields: Union[Dict, None]
        :param crs: Coordinate Reference System
        :type crs: Union[CRS, None]
        :param schema: JSON Schema URI
        :type schema: str
        :return: TFCat
        :rtype: FeatureCollection
        """

        if fields is None:
            fields = dict()

            # get column names and remove the special tfcat feature names (not properties)
            tfcat_colnames = {'feature', 'tmin', 'tmax', 'fmin', 'fmax'}
            colnames = set(table.colnames).difference(tfcat_colnames)
            # complete the fields dictionary
            for col in colnames:
                field = {}
                for k, v in table[col].meta.items():
                    if v is not None:
                        if k == 'options':
                            field['values'] = v
                        else:
                            field[k] = v
                if table[col].unit is not None:
                    field['unit'] = table[col].unit
                if table[col].description is not None:
                    field['info'] = table[col].description
                fields[col] = field

        features = [
            Feature(geometry=row['feature'], properties={key: row[key] for key in fields.keys()}) for row in table
        ]

        return cls(
            features=features,
            properties=properties or table.meta['properties'],
            fields=fields,
            crs=crs or table.meta['crs'],
            schema=schema or table.meta['schema']
        )


class _FeatureColumn(Column):
    """Class for Feature Column

    This class is derived from the astropy Column class, adding new capabilities to
    manage feature geometries.

    :param crs: Coordinate Reference System
    :type crs: Union[CRS, None]
    :param properties: Collection properties
    :type properties: Union[Dict, None]
    :param schema: JSON Schema URI
    :type schema: str
    """

    def __new__(cls, crs=None, properties=None, schema=JSONSCHEMA_URI, **extra):
        self = super().__new__(cls, **extra)
        self._crs = crs or DefaultCRS
        self._properties = properties or {}
        self._schema = schema
        return self

    @property
    def type(self):
        return Column([item['type'] for item in self])

    @property
    def crs(self):
        return self._crs

    @property
    def properties(self):
        return self._properties

    @property
    def schema(self):
        return self._schema

    def coordinates(self, ifeature): #, time_format=None, spectral_unit=None):
        return split_coords(self[ifeature], self._crs)
