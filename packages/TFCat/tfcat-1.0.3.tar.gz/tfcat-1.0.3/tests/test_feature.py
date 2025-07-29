# -*- coding: utf-8 -*-
"""Test TFCat Feature module."""

import pytest
from matplotlib.testing.decorators import image_comparison

from tfcat.feature import Feature, FeatureCollection, _FeatureColumn
from astropy.table import Table as _Table
from tfcat.feature import Table

@pytest.fixture
def feature1():
    """Input Feature #1 params."""
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
            'polar': 'RH'
        }
    }


@pytest.fixture
def feature2():
    """Input Feature #2 params."""
    return {
        'geometry': {
            'coordinates': [
                (653985460.0, 15),
                (653985520.0, 10),
                (653985580.0, 20)
            ],
            'type': 'LineString'
        },
        'properties': {
            'id': 1,
            'polar': 'RH'
        }
    }


@pytest.fixture
def feature_collection():
    """Input Collection params2."""
    return {
        "fields": {
            "id": {
                "info": 'feature id',
                "ucd": "meta.id",
                "datatype": "int"
            },
            "polar": {
                "info": "Polarization",
                "ucd": "phys.polarization",
                "values": ["RH", "LH"],
                "datatype": "str"
            }
        },
        "properties": {
            "author": "Baptiste Cecconi",
            "description": "test collection"
        }
    }


def test_feature(feature1):
    """Test Feature object."""
    feature = Feature(**feature1)
    assert isinstance(feature, Feature)
    assert feature.tmin == 653984460.0
    assert feature.tmax == 653984580.0
    assert feature.fmin == 10
    assert feature.fmax == 20
    assert feature.bbox == (653984460.0, 10.0, 653984580.0, 20.0)
    assert feature.errors() is None
    assert len(feature) == 3


def test_feature_collection(feature1, feature2, feature_collection):
    """Test Feature Collection object."""
    features = [Feature(**feature1), Feature(**feature2)]
    collection = FeatureCollection(features=features, **feature_collection)
    assert isinstance(collection, FeatureCollection)
    assert collection.errors() == []
    assert len(collection) == 2


def test_feature_collection_as_table(feature1, feature2, feature_collection):
    """Test Feature Collection as_table() method."""
    features = [Feature(**feature1), Feature(**feature2)]
    collection = FeatureCollection(features=features, **feature_collection)
    table = collection.as_table()
    assert isinstance(table, _Table)
    assert isinstance(table, Table)
    assert table.colnames == ['feature', 'tmin', 'tmax', 'fmin', 'fmax', 'id', 'polar']
    assert table['polar'].meta['options'] == collection.fields['polar']['values']


def test_feature_collection_from_table(feature1, feature2, feature_collection):
    """Test Feature Collection as_table() method."""
    features = [Feature(**feature1), Feature(**feature2)]
    collection = FeatureCollection(features=features, **feature_collection)
    table = collection.as_table()
    newcoll = FeatureCollection.from_table(table)
    assert dict(newcoll) == collection


def test_feature_column(feature1, feature2, feature_collection):
    """Test FeatureColumn method."""
    features = [Feature(**feature1), Feature(**feature2)]
    collection = FeatureCollection(features=features, **feature_collection)
    table = collection.as_table()
    column = table['feature']
    assert isinstance(column, _FeatureColumn)
    assert all(column.type == ['LineString', 'LineString'])
    assert column.coordinates(0)[0].isot[0] == '1990-09-22T06:21:00.000'


#@image_comparison(baseline_images=['feature_plot'], remove_text=True, extensions=['png'])
#def test_feature_plot(feature1):
#    feature = Feature(**feature1)
#    feature._plot()
#    feature._plot_bbox()
