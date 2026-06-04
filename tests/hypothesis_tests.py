import io

import pytest
from hypothesis import given
from hypothesis.strategies import (
    builds,
    floats,
    integers,
    just,
    lists,
    none,
    one_of,
    tuples,
)

import shapefile as shp

float_nums = floats(allow_nan=False, allow_infinity=False)

point_2D = builds(
    shp.Point, float_nums, float_nums, one_of(none(), integers(min_value=0))
)
pointM = builds(
    shp.PointM,
    float_nums,
    float_nums,
    one_of(none(), float_nums),
    one_of(none(), integers(min_value=0)),
)
pointZ = builds(
    shp.PointZ,
    float_nums,
    float_nums,
    one_of(just(0.0), float_nums),
    one_of(none(), float_nums),
    one_of(none(), integers(min_value=0)),
)


@pytest.mark.hypothesis
@given(expected=point_2D, i=integers(min_value=1))
def test_Point_2D_roundtrips(
    expected: shp.Point,
    i: int,
) -> None:
    stream = io.BytesIO()
    n = shp.Point.write_to_byte_stream(b_io=stream, s=expected, i=i)
    assert n == stream.tell()
    stream.seek(0)
    actual = shp.Point.from_byte_stream(
        shapeType=shp.POINT,
        b_io=stream,
        next_shape_pos=n,
        oid=expected.oid,
        bbox=None,
    )
    assert isinstance(actual, shp.Point)
    assert actual.points == expected.points
    assert actual.oid == expected.oid


@pytest.mark.hypothesis
@given(expected=pointM, i=integers(min_value=1))
def test_Point_M_roundtrips(
    expected: shp.Point,
    i: int,
) -> None:
    stream = io.BytesIO()
    n = shp.PointM.write_to_byte_stream(b_io=stream, s=expected, i=i)
    assert n == stream.tell()
    stream.seek(0)
    actual = shp.PointM.from_byte_stream(
        shapeType=shp.POINTM,
        b_io=stream,
        next_shape_pos=n,
        oid=expected.oid,
        bbox=None,
    )
    assert isinstance(actual, shp.PointM)
    assert actual.points == expected.points
    assert actual.m == expected.m
    assert actual.oid == expected.oid


@pytest.mark.hypothesis
@given(expected=pointZ, i=integers(min_value=1))
def test_Point_Z_roundtrips(
    expected: shp.Point,
    i: int,
) -> None:
    stream = io.BytesIO()
    n = shp.PointZ.write_to_byte_stream(b_io=stream, s=expected, i=i)
    assert n == stream.tell()
    stream.seek(0)
    actual = shp.PointZ.from_byte_stream(
        shapeType=shp.POINTZ,
        b_io=stream,
        next_shape_pos=n,
        oid=expected.oid,
        bbox=None,
    )
    assert isinstance(actual, shp.PointM)
    assert actual.points == expected.points
    assert actual.z == expected.z
    assert actual.m == expected.m
    assert actual.oid == expected.oid


coords_2D_list = lists(tuples(float_nums, float_nums), min_size=1)

multipoint = builds(shp.MultiPoint, points=coords_2D_list)


@pytest.mark.hypothesis
@given(expected=multipoint, i=integers(min_value=1))
def test_MultiPoint_roundtrips(
    expected: shp.MultiPoint,
    i: int,
) -> None:
    stream = io.BytesIO()
    n = shp.MultiPoint.write_to_byte_stream(b_io=stream, s=expected, i=i)
    assert n == stream.tell()
    stream.seek(0)
    actual = shp.MultiPoint.from_byte_stream(
        shapeType=shp.MULTIPOINT,
        b_io=stream,
        next_shape_pos=n,
        oid=expected.oid,
        bbox=None,
    )
    assert isinstance(actual, shp.MultiPoint)
    assert actual.points == expected.points
    assert actual.oid == expected.oid
