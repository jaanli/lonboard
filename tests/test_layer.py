import geopandas as gpd
import numpy as np
import pyarrow as pa
import pytest
import shapely
from traitlets import TraitError

from lonboard import BitmapLayer, Map, ScatterplotLayer
from lonboard.layer_extension import DataFilterExtension


def test_accessor_length_validation():
    """Accessor length must match table length"""
    points = shapely.points([1, 2], [3, 4])
    gdf = gpd.GeoDataFrame(geometry=points)

    with pytest.raises(TraitError, match="same length as table"):
        _layer = ScatterplotLayer.from_geopandas(gdf, get_radius=np.array([1]))

    with pytest.raises(TraitError, match="same length as table"):
        _layer = ScatterplotLayer.from_geopandas(gdf, get_radius=np.array([1, 2, 3]))

    _layer = ScatterplotLayer.from_geopandas(gdf, get_radius=np.array([1, 2]))


def test_accessor_length_validation_extension():
    """Accessor length must match table length"""
    points = shapely.points([1, 2], [3, 4])
    gdf = gpd.GeoDataFrame(geometry=points)
    extension = DataFilterExtension()

    with pytest.raises(TraitError, match="same length as table"):
        _layer = ScatterplotLayer.from_geopandas(
            gdf, extensions=[extension], get_filter_value=np.array([1])
        )

    with pytest.raises(TraitError, match="same length as table"):
        _layer = ScatterplotLayer.from_geopandas(
            gdf, extensions=[extension], get_filter_value=np.array([1, 2, 3])
        )

    _layer = ScatterplotLayer.from_geopandas(
        gdf, extensions=[extension], get_radius=np.array([1, 2])
    )


def test_layer_fails_with_unexpected_argument():
    points = shapely.points([1, 2], [3, 4])
    gdf = gpd.GeoDataFrame(geometry=points)

    with pytest.raises(TypeError, match="Unexpected keyword argument"):
        _layer = ScatterplotLayer.from_geopandas(gdf, unknown_keyword="foo")


def test_layer_outside_4326_range():
    # Table outside of epsg:4326 range
    points = shapely.points([1000000, 2000000], [3000000, 4000000])
    gdf = gpd.GeoDataFrame(geometry=points)

    with pytest.raises(ValueError, match="outside of WGS84 bounds"):
        _layer = ScatterplotLayer.from_geopandas(gdf)


def test_layer_from_geoarrow_pyarrow():
    ga = pytest.importorskip("geoarrow.pyarrow")

    points = gpd.GeoSeries(shapely.points([1, 2], [3, 4]))

    # convert to geoarrow.pyarrow Table (currently requires to ensure interleaved
    # coordinates manually)
    points = ga.with_coord_type(ga.as_geoarrow(points), ga.CoordType.INTERLEAVED)
    table = pa.table({"geometry": points})

    _layer = ScatterplotLayer(table=table)


# Test layer types
def test_bitmap_layer():
    layer = BitmapLayer(
        image="https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-districts.png",
        bounds=[-122.5190, 37.7045, -122.355, 37.829],
    )
    _m = Map(layer)
