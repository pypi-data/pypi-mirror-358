from tfcat.codec import load, loads
from tfcat.geometry import Polygon, MultiPolygon, Point, MultiPoint, LineString, MultiLineString
from tfcat.feature import Feature, FeatureCollection
from tfcat.observation import Observation
from tfcat.validate import validate
from tfcat.crs import CRS
from tfcat.field import Field
import tfcat.utils
from matplotlib import pyplot as plt
from urllib.request import urlopen
from pathlib import Path
from typing import Union


class TFCat:
    """Main TFCat object.

    This object has several constructor methods:

    * :func:`from_file()` to load a TFCat feature collection from a local file.
    * :func:`from_url()` to load a TFCat feature collection from a eremote URL.
    * :func:`__init__()` to directly load a TFCat feature collection object.
    """

    def __init__(
            self,
            tfcat_data: FeatureCollection,
            file_uri: Union[Path, str, None] = None,
    ):
        """
        :param tfcat_data: TFCat feature collection object
        :param file_uri: TFCat file or URL
        """

        self.file = file_uri
        self.data = tfcat_data

    @property
    def data(self) -> FeatureCollection:
        """Returns the internal TFCat data object.

        :return: A TFCat FeatureCollection object
        :rtype: FeatureCollection
        """

        return self._data

    @data.setter
    def data(self, tfcat_data: FeatureCollection):
        self._data = tfcat_data

    @property
    def has_observations(self) -> bool:
        """Informs if the TFCat object has an observation list
        """
        return 'observations' in self._data.keys()

    @property
    def _lookup(self) -> list:
        return list(item.properties['obs_id'] for item in self._data.features)

    @classmethod
    def from_file(cls, file_name: Union[Path, str]):
        """Loads the TFCat feature collection from a local file

        :param file_name: local file path
        :type file_name: Union[Path, str]
        :return: A TFcat object
        :rtype: TFCat
        """
        with open(file_name, 'r') as f:
            tfcat_data = load(f)
        return cls(tfcat_data, file_uri=file_name)

    @classmethod
    def from_url(cls, url: str):
        """Loads the TFCat feature collection from a remote URL

        :param url: remote URL
        :type url: str
        :return: A TFcat object
        :rtype: TFCat
        """
        tfcat_data = loads(urlopen(url).read())
        return cls(tfcat_data, file_uri=url)

    @property
    def crs(self) -> CRS:
        """Returns the Coordinate Reference System.

        The CRS object contains the temporal and spectral axes definitions,
        as well the reference position (where the measurement was done).

        :return: A Coordinate Reference System object
        :rtype: CRS
        """
        return self._data.crs

    @property
    def properties(self) -> dict:
        """Returns the list of TFCat feature collection global properties.

        :return: feature collection properties
        :rtype: dict
        """
        return self._data.properties

    @property
    def fields(self) -> list:
        """Returns the list of Fields objects.

        Fields objects are describing the feature property keywords.

        :return: A list of feature property descriptors
        """
        return self._data.fields

    def __len__(self) -> int:
        """Returns the length of the feature collection.

        The length is the number of features in the TFCat object.

        :returns: number of features
        """
        return len(self._data.features)

    def observation(self, n: int) -> Observation:
        """Returns the nth observation of the TFCat feature collection object.

        :param n: index
        :return: nth observation
        """
        return self._data.observations[n]

    def feature(self, n) -> Feature:
        """Returns the nth feature of the TFCat feature collection object.

        :param n: index
        :type n: int
        :return: nth feature
        :rtype: Feature
        """
        return self._data.features[n]

    @property
    def iter_features(self) -> Feature:
        """Generator on features.

        :return: feature
        """
        n = 0
        while n < len(self):
            yield self.feature(n) #, self.observation(self._lookup[n]) if self.has_observations else None
            n += 1

    @property
    def iter_observations(self) -> Observation:
        """Generator on observations.

        :returns: observation
        """
        n = 0
        while n < len(self._data.observations):
            yield self.observation(n)
#            yield [self.feature(i) for i, x in enumerate(self._lookup) if x == n], self.observation(n)
            n += 1

    def iter_features_by_obs_id(self, obs_id: int) -> Feature:
        """Generator on features within a given obs_id.

        :param obs_id: Observation obs_id
        :returns: Feature
        """
        for i, x in enumerate(self._lookup):
            if x == obs_id:
                yield self.feature(i)

    def validate(self):
        """Validation against the JSON Schema.
        """
        return validate(self._data)

    def _plot_observation(self, oid):
        obs = self.observation(oid)
        crs = self.crs

        bbox_times = [obs.tmin, obs.tmax, obs.tmax, obs.tmin, obs.tmin]
        bbox_times = crs.time_converter(bbox_times).datetime
        bbox_freqs = [obs.fmin, obs.fmin, obs.fmax, obs.fmax, obs.fmin]

        plt.plot(bbox_times, bbox_freqs, '--', label='bbox')

    _plot_style = {
        Point: '+',
        LineString: '-',
        Polygon: '-',
        MultiPoint: '+',
        MultiPolygon: '-',
        MultiLineString: '-',
    }

    def _plot_feature(self, fid):

        feature = self.feature(fid)
        crs = self.crs

        ftype = type(feature.geometry)
        coord = feature['geometry']['coordinates']
        if ftype not in [MultiLineString, MultiPolygon]:
            coord = [coord]
        for item in coord:
            itimes, ifreqs = tfcat.utils.split_coords(item, crs=crs)
            plt.plot(itimes.datetime, ifreqs.value, self._plot_style[ftype], label=f'Feature #{fid}')

    def plot_observation(self, obs_id: int):
        """Plots an observation.

        :param obs_id: observation id
        """
        crs = self.crs

        self._plot_observation(obs_id)

        plt.xlabel(crs.properties['time_coords']['name'])
        plt.ylabel(f"{crs.properties['spectral_coords']['name']} ({crs.properties['spectral_coords']['unit']})")
        plt.title(f'Observation #{obs_id}')

        if obs_id in self._lookup:
            for fid in (i for i, x in enumerate(self._lookup) if x == obs_id):
                self._plot_feature(fid)

        plt.show()

    def plot_feature(self, fid: int):
        """Plots a feature.

        :param fid: feature id

        :raises NotImplemented: if the CRS type is not ``local``.
        """
        from tfcat.crs import TIME_COORDS

        crs = self.crs
        if crs.type == 'local':
            time_coords = crs.properties.get(
                'time_coords',
                TIME_COORDS[crs.properties['time_coords_id']]
            )
        else:
            raise NotImplemented()

        self._plot_feature(fid)

        plt.xlabel("Time")
        plt.ylabel(f"{crs.properties['spectral_coords']['type']} ({crs.properties['spectral_coords']['unit']})")
        plt.title(f'Feature #{fid}')
        plt.show()

    def to_votable(self, file_xml='votable_tfcat.xml'):
        """Exports the TFCat feature collection into VOTable.

        :param file_xml: Output VOTable file name
        :type file_xml: Union[Path, str]
        """

        from astropy.io.votable.tree import Param
        from astropy.io.votable import from_table

        votable = from_table(self._data.as_table())
        table = votable.get_first_table()

        for name, value in self.properties.items():
            # only processing string type properties at this point
            if isinstance(value, str):
                table.params.append(
                    Param(votable, name=name, value=value, arraysize="*", datatype="char")
                )

        votable.to_xml(file_xml)

    def _add_property(self, name: str, values: list, collection_type: str):
        if collection_type in ["features", "observations"]:
            collection_items = getattr(self._data, collection_type)
            if len(values) == len(collection_items):
                for item, value in zip(collection_items, values):
                    item.properties[name] = value
            else:
                raise ValueError("Wrong length of input property values.")

    def add_property(self, name: str, field_def: Field, feature_values=None, observation_values=None):
        """Adds a property to the feature collection.

        The process of adding a property requires providing:

        * the Field definition metadata;
        * the list of property values.

        Properties can be added using this method to features or observations.

        :param name: Name of the property
        :type name: str
        :param field_def: property definition metadata
        :type field_def: Field
        :param feature_values: Property values to be ingested into the feature list.
        :type feature_values: Union[list, None]
        :param observation_values: Property values to be ingested into the observation list.
        :type observation_values: Union[list, None]

        :raises ValueError: If the number of element of the property values is inconsistent with the
        length of the list of feature or observations.
        """
        if not isinstance(field_def, dict):
            raise TypeError('field_def must be a dict')

        self._data.fields[name] = field_def

        if feature_values is not None:
            self._add_property(name, feature_values, "features")
        if observation_values is not None:
            self._add_property(name, observation_values, "observations")
