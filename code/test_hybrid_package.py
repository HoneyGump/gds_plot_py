from shapely.geometry import Polygon, Point

from gdshelpers.geometry.chip import Cell
from gdshelpers.geometry import geometric_union
from gdshelpers.geometry import convert_to_layout_objs

from gdshelpers.helpers import positive_resist

from gdshelpers.parts.port import Port
from gdshelpers.parts.spiral import Spiral
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler

import numpy as np
import gdspy


# # create the cell
# cell = Cell("hybrid_program_test")


# geo1 = Waveguide((0,0), 0, 0.4)
# geo1.add_straight_segment(10)
# geo1_positve = positive_resist.convert_to_positive_resist(geo1, 3)
# cell.add_to_layer(1, geo1)
# cell.add_to_layer(2, geo1_positve)
# cell.save("hybrid.gds")

lib = gdspy.GdsLibrary()
cell_gdspy2 = lib.read_gds("./FocusGC-2.gds")

# cell_gdspy2.add(cell.cell_gdspy)

# geo2 = Spiral((0,0), 0, 0.45, 4, 3, 20)
# geo2_convert = convert_to_layout_objs(geo2.get_shapely_object(), library='gdspy')
# cell_gdspy2.add(geo2_convert)
gdspy.LayoutViewer()


