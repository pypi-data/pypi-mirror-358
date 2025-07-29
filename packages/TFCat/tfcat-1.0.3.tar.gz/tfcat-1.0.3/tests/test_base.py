# -*- coding: utf-8 -*-
"""Test TFCat Base module."""

import pytest

from tfcat.base import Base


@pytest.fixture
def params():
    """Input Base params."""
    return {
        'geometry': {
            'coordinates': [
                (653984460.0, 10),
                (653984520.0, 20),
                (653984580.0, 15)
            ],
            'type': 'LineString'
        },
        'properties': {
            'id': 0,
        }
    }


def test_base(params):
    """Test Base with sample input."""
    assert isinstance(Base(**params), dict)


def test_base_getattr(params):
    """Test Base.__getattr__ with sample input."""
    assert Base(**params).geometry == params['geometry']


def test_base_setattr(params):
    """Test Base.__setattr__ with sample input."""
    cat = Base(**params)
    geo = Base.to_instance(cat.geometry, strict=True)
    geo.type = 'MultiPoint'
    assert geo.type == 'MultiPoint'


def test_base_delattr(params):
    """Test Base.__delattr__ with sample input."""
    cat = Base(**params)
    del cat.type
    assert 'type' not in cat


def test_base_getattr_error(params):
    """Test Base.__getattr__ error with sample input."""
    cat = Base(**params)
    with pytest.raises(AttributeError):
        _ = cat.wrong


def test_base_to_instance(params):
    """Test Base.to_instance with sample input."""
    cat = Base(**params)
    _ = Base.to_instance(cat)

    _ = Base.to_instance(ob=None, default=Base)


def test_base_to_instance_error(params):
    """Test Base.to_instance error with sample input."""
    cat = Base(**params)
    cat.geometry['type'] = 'wrong'

    with pytest.raises(ValueError):
        _ = Base.to_instance(cat.geometry, strict=True)

    _ = Base.to_instance(cat.geometry)


def test_base_type_error(params):
    """Test Base.to_instance error with sample input."""
    cat = Base(**params)
    cat.geometry['type'] = '\u2620\uFE0E' #  u'voil\u00e0' # '\xc3'
    with pytest.raises(TypeError):
        _ = Base.to_instance(cat.geometry)
