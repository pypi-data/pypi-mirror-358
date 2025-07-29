# -*- coding: utf-8 -*-
"""Test TFCat Geometry module."""

import pytest

from tfcat.geometry import (Polygon, Point, LineString, MultiPoint, MultiPolygon, MultiLineString,
                            Geometry, GeometryCollection)


@pytest.fixture
def point():
    return {
        "type": "Point",
        "coordinates": [1158051858, 24730.0]
    }


@pytest.fixture
def linestring():
    return {
        "type": "LineString",
        "coordinates": [
            [1158051858, 24730.0],
            [1158051858, 24735.0]
        ]
    }


@pytest.fixture
def polygon():
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [1158051858, 24730.0],
                [1158051868, 24730.0],
                [1158051868, 24735.0],
                [1158051858, 24735.0],
                [1158051858, 24730.0]
            ]
        ]
    }


@pytest.fixture
def polygon_with_hole():
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [1158051858, 24730.0],
                [1158051868, 24730.0],
                [1158051868, 24735.0],
                [1158051858, 24735.0],
                [1158051858, 24730.0]
            ],
            [
                [1158051860, 24731.0],
                [1158051866, 24731.0],
                [1158051866, 24734.0],
                [1158051860, 24734.0],
                [1158051860, 24731.0]
            ]
        ]
    }


@pytest.fixture
def multipoint():
    return {
        "type": "MultiPoint",
        "coordinates": [
            [1158051858, 24730.0],
            [1158051868, 24735.0],
        ]
    }


@pytest.fixture
def multilinestring():
    return {
        "type": "MultiLineString",
        "coordinates": [
            [
                [1158051858, 24730.0],
                [1158051868, 24735.0],
            ],
            [
                [1158051878, 24740.0],
                [1158051888, 24745.0],
            ]
        ]
    }


@pytest.fixture
def multipolygon():
    return {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [1158051858, 24730.0],
                    [1158051868, 24730.0],
                    [1158051868, 24735.0],
                    [1158051858, 24735.0],
                    [1158051858, 24730.0]
                ]
            ],
            [
                [
                    [1158051878, 24730.0],
                    [1158051888, 24730.0],
                    [1158051888, 24735.0],
                    [1158051878, 24735.0],
                    [1158051878, 24730.0]
                ],
                [
                    [1158051880, 24731.0],
                    [1158051886, 24731.0],
                    [1158051886, 24734.0],
                    [1158051880, 24734.0],
                    [1158051880, 24731.0]
                ]
            ]
        ]
    }


def test_point_geometry(point):
    """Test Point geometry payload."""
    assert Point(**point) == point
    assert Point(**point, validate=True) == point


def test_linestring_geometry(linestring):
    """Test LineString geometry payload."""
    assert LineString(**linestring) == linestring
    assert LineString(**linestring, validate=True) == linestring


def test_polygon_geometry(polygon):
    """Test Polygon geometry payload."""
    assert Polygon(**polygon) == polygon
    assert Polygon(**polygon, validate=True) == polygon
    assert Polygon.from_bbox(
        [polygon["coordinates"][0][0][0], polygon["coordinates"][0][2][0]],
        [polygon["coordinates"][0][0][1], polygon["coordinates"][0][2][1]]
    ) == polygon


def test_polygon_with_hole_geometry(polygon_with_hole):
    """Test Polygon with hole geometry payload."""
    assert Polygon(**polygon_with_hole) == polygon_with_hole
    assert Polygon(**polygon_with_hole, validate=True) == polygon_with_hole


def test_multipoint_geometry(multipoint):
    """Test MultiPoint geometry payload."""
    assert MultiPoint(**multipoint) == multipoint
    assert MultiPoint(**multipoint, validate=True) == multipoint


def test_multilinestring_geometry(multilinestring):
    """Test MultiLineString geometry payload."""
    assert MultiLineString(**multilinestring) == multilinestring
    assert MultiLineString(**multilinestring, validate=True) == multilinestring


def test_multipolygon_geometry(multipolygon):
    """Test MultiPolygon geometry payload."""
    assert MultiPolygon(**multipolygon) == multipolygon
    assert MultiPolygon(**multipolygon, validate=True) == multipolygon


def test_geometry(point):
    """Test Geometry with point input."""
    assert Geometry(**point).type == point['type']
    assert Geometry(**point).coordinates == point['coordinates']


def test_point_geometry_clean_coordinates(point):
    """Test Geometry clean coordinates output."""
    assert Geometry.clean_coordinates(Point(**point), 1) == point['coordinates']
    assert Geometry.clean_coordinates(point['coordinates'], 1) == point['coordinates']
    assert Geometry.clean_coordinates(Geometry(**point), 1) == point['coordinates']
