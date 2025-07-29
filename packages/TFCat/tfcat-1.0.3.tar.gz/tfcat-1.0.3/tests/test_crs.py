# -*- coding: utf-8 -*-
"""Test TFCat CRS module."""

import pytest

from tfcat.crs import DefaultCRS, CRS, TIME_COORDS, SPECTRAL_COORDS
from astropy.time import Time
from astropy.units import Quantity, Unit


@pytest.fixture
def crs_type():
    """Input CRS Type."""
    return "local"


@pytest.fixture
def name():
    """Input CRS Name."""
    return "Time-Frequency"


@pytest.fixture
def time_coords_id():
    """Input CRS time_coords_id."""
    return "unix"


@pytest.fixture
def time_coords_name():
    """Input CRS time_coords_name."""
    return "Timestamp (Unix Time)"


@pytest.fixture
def time_coords_unit():
    """Input CRS time_coords_unit."""
    return "s"


@pytest.fixture
def time_label():
    """Label for time axis."""
    return "Timestamp (Unix Time) [s]"


@pytest.fixture
def time_coords_origin_iso():
    """Input CRS time_coords_origin."""
    return "1970-01-01 00:00:00.000Z"


@pytest.fixture
def time_coords_origin_isot():
    """Input CRS time_coords_origin."""
    return "1970-01-01T00:00:00.000Z"


@pytest.fixture
def time_coords_scale():
    """Input CRS time_coords_scale."""
    return "UTC"


@pytest.fixture
def spectral_coords_id():
    """Input CRS spectral_coords_id."""
    return "Hz"


@pytest.fixture
def spectral_coords_type():
    """Input CRS spectral_coords_name."""
    return "frequency"


@pytest.fixture
def spectral_label():
    """Label for spectral axis."""
    return "frequency [Hz]"


@pytest.fixture
def spectral_coords_unit():
    """Input CRS spectral_coords_name."""
    return "Hz"


@pytest.fixture
def ref_position_id():
    """Input CRS ref_position_id."""
    return "GEOCENTER"


@pytest.fixture
def time_coords_isot(time_coords_name, time_coords_unit, time_coords_origin_isot, time_coords_scale):
    """Input CRS time_coords"""
    return {
        'name': time_coords_name,
        'time_scale': time_coords_scale,
        'time_origin': time_coords_origin_isot,
        'unit': time_coords_unit
    }


@pytest.fixture
def time_coords_iso(time_coords_name, time_coords_unit, time_coords_origin_iso, time_coords_scale):
    """Input CRS time_coords"""
    return {
        'name': time_coords_name,
        'time_scale': time_coords_scale,
        'time_origin': time_coords_origin_iso,
        'unit': time_coords_unit
    }


@pytest.fixture
def payload_time_coords_id(name, crs_type, time_coords_id, spectral_coords_type, spectral_coords_unit, ref_position_id):
    return {
        'type': crs_type,
        'properties': {
            'name': name,
            'time_coords_id': time_coords_id,
            'spectral_coords': {
                'type': spectral_coords_type,
                'unit': spectral_coords_unit
            },
            'ref_position_id': ref_position_id
       }
    }


@pytest.fixture
def payload_time_coords(name, crs_type, time_coords_isot,
                        spectral_coords_type, spectral_coords_unit, ref_position_id):
    return {
        'type': crs_type,
        'properties': {
            'name': name,
            'time_coords': time_coords_isot,
            'spectral_coords': {
                'type': spectral_coords_type,
                'unit': spectral_coords_unit
            },
            'ref_position_id': ref_position_id
       }
    }


@pytest.fixture
def payload_time_coords_iso(name, crs_type, time_coords_iso,
                        spectral_coords_type, spectral_coords_unit, ref_position_id):
    return {
        'type': crs_type,
        'properties': {
            'name': name,
            'time_coords': time_coords_iso,
            'spectral_coords': {
                'type': spectral_coords_type,
                'unit': spectral_coords_unit
            },
            'ref_position_id': ref_position_id
       }
    }


@pytest.fixture
def time_unix_data():
    """test Time data."""
    return [653984460.0, 653984520.0, 653984580.0]


@pytest.fixture
def time_isot_data():
    """test Time data."""
    return ['1990-09-22T06:21:00.000', '1990-09-22T06:21:00.000', '1990-09-22T06:21:00.000']


@pytest.fixture
def frequency_data():
    """test frequency data."""
    return 1


def test_crs_dict_payload(payload_time_coords_id):
    """Test CRS payload."""
    assert CRS(payload_time_coords_id) == payload_time_coords_id


def test_crs_direct_payload(payload_time_coords_id):
    """Test CRS payload."""
    assert CRS(**payload_time_coords_id) == payload_time_coords_id


def test_crs_configure_payload_time_coords_id(name, time_coords_id, spectral_coords_id, ref_position_id, payload_time_coords_id):
    """Test CRS payload."""
    assert CRS.configure(
        crs_name=name,
        time_coords_id=time_coords_id,
        spectral_coords_id=spectral_coords_id,
        ref_position_id=ref_position_id
    ) == payload_time_coords_id


def test_crs_configure_payload_time_coords(name, time_coords_isot, spectral_coords_id, ref_position_id, payload_time_coords):
    """Test CRS payload."""
    assert CRS.configure(
        crs_name=name,
        time_coords=time_coords_isot,
        spectral_coords_id=spectral_coords_id,
        ref_position_id=ref_position_id
    ) == payload_time_coords


def test_crs_configure_payload_time_coords_id__error(time_coords_id, time_coords_iso, spectral_coords_id,
                                                     ref_position_id, payload_time_coords_id):
    """Test CRS payload."""
    with pytest.raises(ValueError):
        CRS.configure(
            time_coords_id=time_coords_id,
            time_coords=time_coords_iso,
            spectral_coords_id=spectral_coords_id,
            ref_position_id=ref_position_id
        )


def test_crs_default_payload(payload_time_coords_id):
    """Test CRS payload."""
    assert DefaultCRS == payload_time_coords_id


def test_time_converter(time_unix_data, payload_time_coords_id):
    """Test CRS payload with UNIX time data."""
    crs = CRS(payload_time_coords_id)
    assert isinstance(crs.time_converter(time_unix_data), Time)
    assert len(crs.time_converter(time_unix_data)) == len(time_unix_data)
    assert crs.time_converter(time_unix_data).isot[0] == '1990-09-22T06:21:00.000'


def test_time_converter_error(time_isot_data, payload_time_coords_id):
    """Test CRS payload with ISO time data."""
    crs = CRS(payload_time_coords_id)
    with pytest.raises(ValueError):
        crs.time_converter(time_isot_data)


def test_spectral_converter(frequency_data, payload_time_coords_id):
    """Test CRS payload with frequency data."""
    crs = CRS(payload_time_coords_id)
    assert isinstance(crs.spectral_converter(frequency_data), Quantity)
    assert crs.spectral_converter(frequency_data).value == frequency_data
    assert Unit(crs.spectral_converter(frequency_data).unit) == Unit(crs['properties']['spectral_coords']['unit'])


def test_convert1(time_unix_data, frequency_data, time_coords_id, spectral_coords_unit, payload_time_coords_id):
    """Test CRS payload converter (time_coords_id)."""
    crs = CRS(payload_time_coords_id)
    point = (time_unix_data, frequency_data)
    tconv, fconv = crs.converter(point)
    for t0, t1 in zip(tconv, Time(time_unix_data, format=time_coords_id)):
        assert t0 == t1
    assert fconv == frequency_data * Unit(spectral_coords_unit)


def test_convert1_iso(payload_time_coords_iso, time_unix_data, frequency_data, time_coords_id):
    """Test CRS payload converter (time_coords) with ISO time (not ISOT)."""
    crs = CRS(payload_time_coords_iso)
    point = (time_unix_data, frequency_data)
    tconv, fconv = crs.converter(point)
    for t0, t1 in zip(tconv, Time(time_unix_data, format=time_coords_id)):
        assert t0.unix == pytest.approx(t1.unix)



def test_convert2(time_unix_data, frequency_data, time_coords_id, spectral_coords_unit, payload_time_coords):
    """Test CRS payload converter (time_coords)."""
    crs = CRS(payload_time_coords)
    point = (time_unix_data, frequency_data)
    tconv, fconv = crs.converter(point)
    for t0, t1 in zip(tconv, Time(time_unix_data, format=time_coords_id)):
        assert t0.unix == pytest.approx(t1.unix)
    assert fconv == frequency_data * Unit(spectral_coords_unit)


def test_time_coords(time_coords_id, payload_time_coords_id):
    crs = CRS(payload_time_coords_id)
    assert crs.time_coords == TIME_COORDS[time_coords_id]


def test_spectral_coords(spectral_coords_id, payload_time_coords_id):
    crs = CRS(payload_time_coords_id)
    assert crs.spectral_coords == SPECTRAL_COORDS[spectral_coords_id]


def test_labels(payload_time_coords_id, time_label, spectral_label):
    crs = CRS(payload_time_coords_id)
    assert crs.time_label == time_label
    assert crs.spectral_label == spectral_label
