from gdshelpers.geometry.chip import Cell
from shapely.geometry import Polygon, Point
from gdshelpers.parts.port import Port
from gdshelpers.parts.spiral import Spiral
from gdshelpers.parts.waveguide import Waveguide
import numpy as np
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.geometry import geometric_union


l_wg = 50
gap=3
w_wg = 0.44

coupler_params = {
        'width': w_wg,
        'full_opening_angle': np.deg2rad(40),
        'grating_period': 0.64,
        'grating_ff': 0.546875,
        'n_gratings': 20,
        'taper_length': 16,
}

left_gc = GratingCoupler.make_traditional_coupler(origin=(0, 0), **coupler_params, angle=-np.pi/2)

left_wg = Waveguide.make_at_port(left_gc.port)
left_wg.add_straight_segment(l_wg) 

radius_bend = 10
left_bend = Waveguide.make_at_port(left_wg.port)
left_bend.add_bend(np.pi/2, radius_bend) 

left_wg2 = Waveguide.make_at_port(left_bend.port)
left_wg2.add_straight_segment(127) 

spiral = Spiral.make_at_port(left_wg2.current_port, num=16, gap=gap, inner_gap=30)
length = spiral.length
print(length)

right_bend = Waveguide.make_at_port(spiral.out_port)
right_bend.add_bend(-np.pi/2, radius_bend) 

right_wg = Waveguide.make_at_port(right_bend.port)
right_wg.add_straight_segment(l_wg-gap-w_wg) 
right_coupler = GratingCoupler.make_traditional_coupler_at_port(right_wg.current_port, **coupler_params)

device = geometric_union([left_gc, left_wg, left_wg2, left_bend, spiral, right_bend, right_wg, right_coupler])
buffer_device = device.buffer(3)
buffer_not_device = buffer_device.difference(device)

cell = Cell('CELL')
cell.add_to_layer(1, left_gc, left_wg, left_wg2, left_bend, spiral, right_bend, right_wg, right_coupler)  # blue
cell.add_to_layer(2, buffer_not_device)  # blue


cell.save('chip.gds')