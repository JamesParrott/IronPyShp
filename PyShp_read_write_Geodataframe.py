"""
Shapefile to/from Geopandas GeoDataframe converters

Adapted from Martin Fleis's PyShp branch of his Geopandas fork
https://github.com/martinfleis/geopandas/blob/4a2bfbbc4781dba21e7da29b538149cd68052eb5/geopandas/io/file.py
"""
import io
import warnings


def _read_pyshp(filename, encoding="ISO-8859-1", encoding_errors="strict"):
    """Shapefile to Geopandas GeoDataframe converter"""
    import shapefile
    from geopandas import GeoDataFrame
    import pyproj

    try:
        with open(filename[:-3] + "cpg", "r") as cpg:
            encoding = cpg.read()
    except FileNotFoundError:
        pass

    try:
        shp = shapefile.Reader(
            filename, encoding=encoding, encodingErrors=encoding_errors
        )
        records = shp.shapeRecords()
    except UnicodeDecodeError:
        import chardet

        # guess encoding
        with open(filename[:-3] + "dbf", "rb") as dbf:
            encoding = chardet.detect(dbf.read())["encoding"]
        shp = shapefile.Reader(filename, encoding=encoding, encodingErrors="replace")
        records = shp.shapeRecords()

    # fetch CRS
    try:
        with open(filename[:-3] + "prj", "r") as crs_wkt:
            crs = pyproj.CRS.from_wkt(crs_wkt.read())
    except FileNotFoundError:
        crs = None

    shp.close()
    return GeoDataFrame.from_features(records.__geo_interface__, crs=crs)


def _write_pyshp(
    df, filename, index=False, encoding="ISO-8859-1", encoding_errors="strict"
):
    """
    Geopandas GeoDataframe to Shapefile converter

    Missing:
    - specification of field size (precision, lenght)
    """
    import shapefile

    if any([len(c) > 10 for c in df.columns.tolist()]):
        warnings.warn(
            "Column names longer than 10 characters will be truncated when saved to "
            "ESRI Shapefile.",
            stacklevel=2,
        )

    fields_mapping = {
        "i": "N",
        "u": "N",
        "f": "N",
        "c": "N",
        "M": "D",
        "O": "C",
        "b": "L",
        "S": "C",
        "U": "C",
    }

    geometry = df.geometry
    data = df.drop(columns="geometry")
    if index:
        data = data.reset_index()

    with shapefile.Writer(
        filename, encoding=encoding, encodingErrors=encoding_errors
    ) as w:
        for name, dtype in data.dtypes.iteritems():
            w.field(str(name), fields_mapping[dtype.kind])

        for t in data.itertuples(index=False):
            w.record(*t)

        for geom in geometry:
            if geom is None:
                w.null()
            elif geom.type == "Point":
                if geom.has_z:
                    w.pointz(geom.x, geom.y, geom.z)
                else:
                    w.point(geom.x, geom.y)
            elif geom.type == "MultiPoint":
                if geom.has_z:
                    w.multipointz(np.asarray(geom))
                else:
                    w.multipoint(np.asarray(geom))
            elif geom.type == "LineString":
                if geom.has_z:
                    w.linez([list(geom.coords)])
                else:
                    w.line([list(geom.coords)])
            elif geom.type == "MultiLineString":
                if geom.has_z:
                    w.linez([list(g.coords) for g in geom.geoms])
                else:
                    w.line([list(g.coords) for g in geom.geoms])
            elif geom.type == "Polygon":
                c = []
                c.append(list(geom.exterior.coords))
                for i in geom.interiors:
                    c.append(list(i.coords))
                if geom.has_z:
                    w.polyz(c)
                else:
                    w.poly(c)
            elif geom.type == "MultiPolygon":
                c = []
                for g in geom.geoms:
                    c.append(list(g.exterior.coords))
                    for i in g.interiors:
                        c.append(list(i.coords))
                if geom.has_z:
                    w.polyz(c)
                else:
                    w.poly(c)
            elif geom.type == "GeometryCollection":
                raise ValueError(
                    "Geometry type of 'Geometry Collection' is not supported in SHP."
                )
            else:
                w.null()

    # write CRS to .prj
    if df.crs:
        with open(filename[:-3] + "prj", "w") as prj:
            prj.write(df.crs.to_wkt(version="WKT1_ESRI"))

    # write encoding to .cpg
    with open(filename[:-3] + "cpg", "w") as cpg:
        cpg.write(encoding)
