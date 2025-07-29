# -*- coding: utf-8 -*-
"""Test TFCat tfcat module"""

import pytest
from pathlib import Path

from typing import Generator
from tfcat import TFCat, FeatureCollection, CRS, Feature


@pytest.fixture
def tfcat_test_file():
    """TFCat test file"""
    return Path(__file__).parent / "data" / "tfcat.json"


@pytest.fixture
def tfcat_test_votable_file():
    """TFCat test votable file"""
    return Path(__file__).parent / "data" / "votable_tfcat.xml"


@pytest.fixture
def tfcat_test_object_from_file(tfcat_test_file):
    """TFCat test object from file"""
    return TFCat.from_file(tfcat_test_file)


@pytest.fixture
def tfcat_test_votable_content(tfcat_test_votable_file):
    """TFCat test votable object"""
    with open(tfcat_test_votable_file, "r") as f:
        votable = f.readlines()
    return votable


@pytest.fixture
def tfcat_test_url():
    return "http://maser.obspm.fr/data/maser4py/tests/data/maser/tfcat/tfcat.json"


@pytest.fixture
def tfcat_test_object_from_url(tfcat_test_url):
    """TFCat test object from file"""
    return TFCat.from_url(tfcat_test_url)


def test_tfcat_from_file(tfcat_test_object_from_file):
    """Test TFCat from_file class method."""
    assert isinstance(tfcat_test_object_from_file, TFCat)


def test_tfcat_from_url(tfcat_test_object_from_url):
    """Test TFCat from_url class method."""
    assert isinstance(tfcat_test_object_from_url, TFCat)


def test_tfcat_file(tfcat_test_object_from_file, tfcat_test_file):
    """Test TFCat file property."""
    assert tfcat_test_object_from_file.file == tfcat_test_file


def test_tfcat_data(tfcat_test_object_from_file):
    """Test TFCat data property."""
    assert isinstance(tfcat_test_object_from_file.data, FeatureCollection)


def test_tfcat_crs(tfcat_test_object_from_file):
    """Test TFCat crs attribute."""
    assert isinstance(tfcat_test_object_from_file.crs, CRS)


def test_tfcat_properties(tfcat_test_object_from_file):
    """Test TFCat properties attribute."""
    assert isinstance(tfcat_test_object_from_file.properties, dict)
    assert set(tfcat_test_object_from_file.properties.keys()) == {
        "facility_name",
        "instrument_name",
        "receiver_name",
        "title",
    }


def test_tfcat_fields(tfcat_test_object_from_file):
    """Test TFCat fields attribute."""
    assert isinstance(tfcat_test_object_from_file.fields, dict)
    assert set(tfcat_test_object_from_file.fields.keys()) == {
        "quality",
    }


def test_tfcat_len(tfcat_test_object_from_file):
    """Test TFCat __len__ method."""
    assert len(tfcat_test_object_from_file) == 2


def test_tfcat_feature(tfcat_test_object_from_file):
    """Test TFCat feature method."""
    assert isinstance(tfcat_test_object_from_file.feature(0), Feature)


def test_tfcat_iter_features(tfcat_test_object_from_file):
    """Test TFCat iter_features attribute."""
    iter = tfcat_test_object_from_file.iter_features
    assert isinstance(iter, Generator)
    assert isinstance(next(iter), Feature)
    assert isinstance(next(iter), Feature)


def test_tfcat_add_property(tfcat_test_object_from_file):
    """Test TFCat add_property method."""
    tfcat_test_object_from_file.add_property(
        name="test",
        field_def={"info": "Test property", "ucd": "meta.cryptic", "datatype": "str"},
        feature_values=["test_0", "test_1"]
    )
    assert set(tfcat_test_object_from_file.fields.keys()) == {
        "quality",
        "test",
    }
    assert set(tfcat_test_object_from_file.feature(0).properties.keys()) == {
        "quality",
        "test",
    }


def test_tfcat_add_property_error(tfcat_test_object_from_file):
    """Test TFCat add_property method error."""
    with pytest.raises(TypeError):
        tfcat_test_object_from_file.add_property(
            name="test",
            field_def="test",
            feature_values=["test_0", "test_1"]
        )


def test_tfcat_to_votable(tfcat_test_object_from_file, tfcat_test_votable_content):
    """Test TFCat to_votable method."""
    tmp_file = Path("/tmp/votable_tfcat.xml")
    tfcat_test_object_from_file.to_votable(file_xml=str(tmp_file))
    with open(tmp_file, "r") as f:
        votable = f.readlines()
    assert votable == tfcat_test_votable_content
    tmp_file.unlink()
