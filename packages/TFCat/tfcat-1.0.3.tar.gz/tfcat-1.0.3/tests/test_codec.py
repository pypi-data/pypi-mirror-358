# -*- coding: utf-8 -*-
"""Test TFCat Codec module."""

import pytest

import json
from io import StringIO
from tfcat.codec import dump, dumps, load, loads


@pytest.fixture
def params():
    """Input Base params."""
    return {
        'coordinates': [
            (653984460.0, 10),
            (653984520.0, 20),
            (653984580.0, 15)
        ],
        'type': 'LineString'
    }


def test_loads(params):
    assert loads(json.dumps(params)).is_valid is True


def test_load(params):
    with StringIO() as f:
        f.write(json.dumps(params))
        f.seek(0)
        assert load(f).is_valid is True


def test_dump(params):
    with StringIO() as f:
        dump(params, f)


def test_dumps(params):
    _ = (dumps(params))


def test_error(params):
    import numpy
    p = params.copy()
    p['coordinates'].append((numpy.float64(653984480.0), 10))
    _ = (dumps(p))

