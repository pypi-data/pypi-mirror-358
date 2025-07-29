from tfcat.base import Base
from astropy.time import Time
from astropy.units import Unit, Quantity
from typing import Union


class CRS(Base):
    """The coordinate reference system (CRS) is a
    time-frequency coordinate reference system, which consists in a temporal
    coordinate reference system and a spectral coordinate reference system. It
    also defines the CRS reference position.

    A CRS object can be of three types: ``local``, ``link`` or ``name``.
    In this version, solely the ``local`` value is implemented, so that the
    ``link`` and ``name`` SHOULD not be used.

    CRS objects can be instantiated with two methods:

    * :func:`__init__()`: direct construct method.
    * :func:`configure()`: user-friendly construct method.

    :param crs: CRS metadata (compliant with the CRS JSON schema section)
    :type crs: dict
    :param type: Type of CRS (``local``, ``link`` or ``name``). Default is ``local``.
    :type type: str
    :param properties: CRS properties (compliant with the corresponding CRS JSON schema section)
    :type properties: dict
    :returns: a CRS Object
    :rtype: CRS
    """

    def __init__(self, crs=None, type="local", properties=None, **extra):
        super(CRS).__init__(**extra)
        if crs is not None:
            self['type'] = crs['type']
            self['properties'] = crs['properties']
        if properties is not None:
            self['type'] = type
            self['properties'] = properties

    @property
    def time_label(self):
        return f"{self.time_coords['name']} [{self.time_coords['unit']}]"

    @property
    def spectral_label(self):
        return f"{self.spectral_coords['type']} [{self.spectral_coords['unit']}]"

    @property
    def time_coords(self) -> dict:
        return self['properties'].get('time_coords', TIME_COORDS[self['properties']['time_coords_id']])

    @property
    def spectral_coords(self) -> dict:
        return self['properties']['spectral_coords']

    @classmethod
    def configure(
            cls,
            spectral_coords_id: str,
            ref_position_id: str,
            time_coords=None,
            time_coords_id=None,
            crs_name=None
    ):
        """Configures a local CRS object.

        Configuring a local CRS requires to define the temporal and spectral axes, and a reference position.

        The temporal axis is configured either with the ``time_coords_id`` parameter, or with the ``time_coords``
        parameter. Those two input parameters can't be set simultaneously. The ``time_coords_id`` allowed values
        (and associated definitions) are listed below:

        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``time_coords_id``  | name                        | unit | time origin                   | scale |
        +=====================+=============================+======+===============================+=======+
        | ``unix``            | Timestamp (Unix Time)       | s    | ``1970-01-01T00:00:00.000Z``  | UTC   |
        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``jd``              | Julian Day                  | d    | ``-4712-01-01T12:00:00.000Z`` | UTC   |
        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``mjd``             | Modified Julian Day         | d    | ``1858-11-17T00:00:00.000Z``  | UTC   |
        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``mjd_cnes``        | Modified Julian Day         | d    | ``1950-01-01T00:00:00.000Z``  | UTC   |
        | `                   | (CNES definition)           |      |                               |       |
        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``mjd_nasa``        | Modified Julian Day         | d    | ``1968-05-24T00:00:00.000Z``  | UTC   |
        |                     | (NASA definition)           |      |                               |       |
        +---------------------+-----------------------------+------+-------------------------------+-------+
        | ``cdf_tt2000``      | CDF Epoch TT2000            | ns   | ``2000-01-01T00:00:00.000Z``  | TT    |
        +---------------------+-----------------------------+------+-------------------------------+-------+

        The other way to define the temporal axis is to provide the definition metadata, as defined in the
        CRS TFCat specification:

        * ``name``: The name of the CRS
        * ``unit``: unit for the time axis, e.g., ``s``
        * ``time_origin``: time reference point in ISO-8601 format, e.g., ``1970-01-01T00:00:00.000Z``.
        * ``time_scale``: time scale in use, with values taken from https://www.ivoa.net/rdf/timescale/

        The spectral axis is configured with the ``spectral_coords_id`` parameter. The allowed values
        (and their associated definition) are listed in the following table:

        +------------------------+------------+---------------+
        | ``spectral_coords_id`` | scale type | unit          |
        +========================+============+===============+
        | ``Hz``                 | frequency  | Hz            |
        +------------------------+------------+---------------+
        | ``kHz``                | frequency  | kHz           |
        +------------------------+------------+---------------+
        | ``MHz``                | frequency  | MHz           |
        +------------------------+------------+---------------+
        | ``m``                  | wavelength | m             |
        +------------------------+------------+---------------+
        | ``cm``                 | wavelength | cm            |
        +------------------------+------------+---------------+
        | ``mm``                 | wavelength | mm            |
        +------------------------+------------+---------------+
        | ``cm-1``               | wavenumber | cm :sup:`-1`  |
        +------------------------+------------+---------------+
        | ``eV``                 | energy     | eV            |
        +------------------------+------------+---------------+

        The reference position is the location of the underlying measurement used to produce
        the catalogue. It is a named position: an item from the RefPosition vocabulary
        maintained by IVOA (https://www.ivoa.net/rdf/refposition), a named spacecraft (e.g.,
        ``wind`` or ``juno``) or a named observatory (``nancay-decameter-array``, ``lofar``,
        ``lwa``). For values not in the RefPosition vocabulary, we recommend to use lower case,
        dashed separated, names, until an observation facility vocabulary is available.

        :param spectral_coords_id: Spectral coordinate id (see table above for allowed values)
        :type spectral_coords_id: str
        :param ref_position_id: Named reference position.
        :type ref_position_id: str
        :param time_coords: Dictionary containing the relevant temporal axis definition.
        :type time_coords: Union[dict, None]
        :param time_coords_id: Temporal coordinate id (see table above for allowed values)
        :type time_coords_id: Union[str, None]
        :param crs_name: Name of the CRS (free text)
        :type crs_name: Union[str, None]
        :returns: a CRS Object
        :rtype: CRS
        :raises ValueError: if ``time_coords`` and ``time_coords_id`` are set simultaneously.
        """

        if time_coords is not None and time_coords_id is not None:
            raise ValueError("TFCat CRS input parameters error: Either 'time_coords' or 'time_coords_id' must be set.")

        crs = {
            'type': "local",
            'properties': {
                'spectral_coords': SPECTRAL_COORDS[spectral_coords_id],
                'ref_position_id': ref_position_id,
            }
        }
        if crs_name is not None:
            crs["properties"]["name"] = crs_name

        if time_coords_id in time_mapping.keys():
            crs["properties"]["time_coords_id"] = time_coords_id
        else:
            crs["properties"]["time_coords"] = time_coords
        return CRS(crs=crs)

    def time_converter(self, x) -> Time:
        """Converts time coordinate into an ``astropy.time.Time`` object.

        :return: astropy Time object
        :rtype: astropy.time.Time
        """
        if 'time_coords_id' in self.properties.keys():
            return time_mapping[self.properties['time_coords_id']](x)
        else:
            return self._custom_time_converter(x)

    def spectral_converter(self, x) -> Quantity:
        """Converts spectral coordinate into an ``astropy.units.Quantity`` object.

        :return: astropy Quantity object
        :rtype: astropy.units.Quantity
        """
        return x * Unit(self.properties['spectral_coords']['unit'])

    def converter(self, x):
        """Converts a pair of coordinates into a tuple of (``astropy.time.Time``,
        ``astropy.units.Quantity``).

        :return: coordinate tuple
        :rtype: tuple(astropy.time.Time, astropy.units.Quantity)
        """
        return self.time_converter(x[0]), self.spectral_converter(x[1])

    def _custom_time_converter(self, t):
        time_coords = self.properties['time_coords']
        time_origin = time_coords['time_origin']
        if 'T' in time_origin:
            time_format = 'isot'
        else:
            time_format = 'iso'
        return Time(
            time_origin,
            format=time_format,
            scale=time_coords['time_scale'].lower()
        ) + t * Unit(time_coords['unit'])

time_mapping = {
    'unix': lambda t: Time(t, format="unix"),
    'jd': lambda t: Time(t, format='jd'),
    'mjd': lambda t: Time(t, format='mjd'),
    'mjd_cnes': lambda t: Time("1950-01-01T00:00:00.000Z", format='iso') + t * Unit('d'),
    'mjd_nasa': lambda t: Time("1968-05-24T00:00:00.000Z", format='iso') + t * Unit('d'),
    'iso': lambda t: Time(t, format='iso'),
    'cdf_tt2000': lambda t: Time('2000-01-01 00:00:00.000Z', format='iso') + t * Unit('ns')
}

TIME_COORDS = {
    'unix': {
        "name": "Timestamp (Unix Time)",
        "unit": "s",
        "time_origin": "1970-01-01T00:00:00.000Z",
        "time_scale": "UTC"
    },
    'jd': {
        "name": "Julian Day",
        "unit": "d",
        "time_origin": "-4712-01-01T12:00:00.000Z",
        "time_scale": "UTC"
    },
    'mjd': {
        "name": "Modified Julian Day",
        "unit": "d",
        "time_origin": "1858-11-17T00:00:00.000Z",
        "time_scale": "UTC"
    },
    'mjd_cnes': {
        "name": "Modified Julian Day (CNES definition)",
        "unit": "d",
        "time_origin": "1950-01-01T00:00:00.000Z",
        "time_scale": "UTC"
    },
    'mjd_nasa': {
        "name": "Modified Julian Day (NASA definition)",
        "unit": "d",
        "time_origin": "1968-05-24T00:00:00.000Z",
        "time_scale": "UTC"
    },
    'cdf_tt2000': {
        "name": "CDF Epoch TT2000",
        "unit": "ns",
        "time_origin": "2000-01-01 00:00:00.000Z",
        "time_scale": "TT"
    }
}

SPECTRAL_COORDS = {
    'Hz': {
        "type": "frequency",
        "unit": "Hz"
    },
    'kHz': {
        "type": "frequency",
        "unit": "kHz"
    },
    'MHz': {
        "type": "frequency",
        "unit": "MHz"
    },
    'm': {
        "type": "wavelength",
        "unit": "m"
    },
    'cm': {
        "type": "wavelength",
        "unit": "cm"
    },
    'mm': {
        "type": "wavelength",
        "unit": "mm"
    },
    'cm-1': {
        "type": "wavenumber",
        "unit": "cm**-1"
    },
    'eV': {
        "type": "energy",
        "unit": "eV"
    },
}

REF_POSITION = [
    'GEOCENTER',
]

DefaultCRS = CRS({
    "type": "local",
    "properties": {
        "name": "Time-Frequency",
        "time_coords_id": 'unix',
        "spectral_coords": SPECTRAL_COORDS['Hz'],
        "ref_position_id": 'GEOCENTER',
    }
})
