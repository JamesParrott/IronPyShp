import shapefile

with shapefile.Reader("tests/shapefiles/blockgroups.shp") as source:
    fields = source.fields[1:]
    selected = [
        (shape, record)
        for shape, record in zip(source.shapes(), source.records())
        if record[0] == "active"
    ]

    with shapefile.Writer("active.shp") as target:
        target.fields = fields
        for shape, record in selected:
            target.shape(shape)
            target.record(*record)

    with shapefile.Reader("active") as r:
        assert len(r) == 0
        assert r.shapeType == 0
        assert r.shapeType != source.shapeType # (it should be 5)




