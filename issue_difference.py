from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.spiral import Spiral
from gdshelpers.geometry import geometric_union

# create the spiral
spiral = Spiral(origin=(0,0), angle=0, width=0.45, num=16, gap=3, inner_gap=30)

# get the shapely 
device = geometric_union([spiral])
# Boolean operation: difference
buffer_device = device.buffer(3)
buffer_not_device = buffer_device.difference(device)

cell = Cell('cell_difference')
cell.add_to_layer(1, buffer_not_device)
# Here don't use cell.show() to verify the issue, and use cell.save() please.
cell.save('gdshelpers_difference.gds')


# And I found it's OK if I use "not" from gdspy.boolean()
from gdshelpers.geometry import convert_to_layout_objs
import gdspy
# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)

# create a new cell to save 
cell_gdspy = lib.new_cell("cell_not_gdspy")

geo1 = convert_to_layout_objs(buffer_device,library='gdspy')
geo2 = convert_to_layout_objs(device,library='gdspy')
inv = gdspy.boolean(geo1, geo2, "not")

cell_gdspy.add(inv)
lib.write_gds("gdspy_not.gds")

