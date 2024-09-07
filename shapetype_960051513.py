import shapefile as shp

shapefile_name = 'delete_me'

w = shp.Writer(shapefile_name)

w.field('name', 'C')

# Give sufficient size to the file, otherwise reading it 
# before the writer closes will error on reading a 32 
# byte header in the dbf
for i in range(3200):
    w.poly([0, 0]) 
    w.record(f'point_{i}')


r = shp.Reader(shapefile_name)

print(f'{r.shapeType=}')

assert r.shapeType == 960051513

