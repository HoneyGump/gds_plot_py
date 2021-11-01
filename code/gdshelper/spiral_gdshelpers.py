from shapely.geometry import Polygon, Point

from gdshelpers.geometry.chip import Cell
from gdshelpers.geometry import geometric_union
# from gdshelpers.geometry import convert_to_layout_objs

from gdshelpers.helpers import positive_resist

from gdshelpers.parts.port import Port
from gdshelpers.parts.spiral import Spiral
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.text import Text
from gdshelpers.parts.coupler import _example

import numpy as np
import gdspy



gap = 3
w_wg = 0.5

def spiral_with_coupler(cell, origin=(0, 0), width=0.5, angle=0, gap=3, num=4):
        l_wg = 100

        left_wg = Waveguide(origin, angle, width)
        left_wg.add_straight_segment(l_wg) 

        spiral = Spiral.make_at_port(left_wg.current_port, num=num, gap=gap, inner_gap=30)
        print(spiral.length, "um")
        print(spiral.out_port)
        right_wg = Waveguide.make_at_port(spiral.out_port)
        right_wg.add_straight_segment(l_wg) 

        layout = positive_resist.convert_to_positive_resist([left_wg, spiral, right_wg], gap, outer_resolution=1e-3)

        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon1 = Polygon(outer_corners)
        origin = spiral.out_port.origin
        origin[0] = origin[0] + l_wg + 2*gap
        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon2 = Polygon(outer_corners)
        polygon = polygon1.union(polygon2)

        layout_fixed = layout.difference(polygon)

        cell.add_to_layer(1, layout_fixed)

        # add the text of the length of spiral
        cell.add_to_layer(101, Text((origin[0], origin[1]-50), 20, str(spiral.length) ) )

def coupler_coupler(origin, width=0.5, angle=0, gap=3):
        l_wg = 100

        left_wg = Waveguide(origin, angle, width)
        left_wg.add_straight_segment(l_wg) 

        right_wg = Waveguide.make_at_port(left_wg.port)
        right_wg.add_straight_segment(l_wg) 

        layout = positive_resist.convert_to_positive_resist([left_wg, right_wg], gap, outer_resolution=1e-3)

        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon1 = Polygon(outer_corners)
        origin = (origin[0] + 2*l_wg + 2*gap, origin[1])
        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon2 = Polygon(outer_corners)
        polygon = polygon1.union(polygon2)

        layout_fixed = layout.difference(polygon)

        cell.add_to_layer(1, layout_fixed)
        

cell = Cell('CELL')
# spiral_with_coupler(cell, origin=(0,0), gap=3, num=10)
# spiral_with_coupler(cell, origin=(0,200), gap=3, num=15)
# spiral_with_coupler(cell, origin=(0,850), gap=3, num=64)

# coupler_coupler((0, -150))
# coupler_coupler((0, -300))
w_wg = 0.5
w_GC = 10
l_taper = 500
l_wg = 100
l_GC = 100
origin = 0
taperVector = [(origin, -w_wg/2), (origin, w_wg/2), (origin+l_taper, w_GC/2), (origin+l_taper+l_GC, w_GC/2), (origin+2*l_taper+l_GC, w_wg/2), (origin+2*l_taper+l_GC, -w_wg/2), (origin+l_taper+l_GC, -w_GC/2), (origin+l_taper, -w_GC/2),(origin, -w_wg/2)]
taperGCTaper = Polygon(taperVector)
taperGCTaper2 = positive_resist.convert_to_positive_resist([taperGCTaper], 3, outer_resolution=1e-3)
cell.add_to_layer(1, taperGCTaper2)

# _example()
cell.save("./taper.gds")
# cell.start_viewer()