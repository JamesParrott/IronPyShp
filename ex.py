import io

import shapefile as shp

shp_stream, dbf_stream = io.BytesIO(), io.BytesIO()

with shp.DbfWriter(dbf_stream) as w:
    w.field("Text_field")
    w._record(["0 0 0"], set_deletion_flag=True)
    w._record(["1 1 1"], set_deletion_flag=False)

with shp.ShpWriter(shp_stream) as w:
    w.shape(shp.PointZ(0,0,0))
    w.shape(shp.PointZ(1,1,1))

with shp.Reader(shp=shp_stream, dbf=dbf_stream) as r:
    for i, sr in enumerate(r.iterShapeRecords()):
        print(f"{i}) Shape: {sr.shape.points_3D}, Rec: {sr.record})")