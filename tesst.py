from math import pi
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.resonator import RingResonator


left_coupler = GratingCoupler.make_traditional_coupler_from_database([0, 0], 1, 'sn330', 1550)
wg1 = Waveguide.make_at_port(left_coupler.port)
wg1.add_straight_segment(length=10)
wg1.add_bend(-pi/2, radius=70)
wg1.add_straight_segment(length=75)

ring_res = RingResonator.make_at_port(wg1.current_port ,gap=(0.5, 4), radius=30,straight_feeding=True, draw_opposite_side_wg=True)


wg2 = Waveguide.make_at_port(ring_res.port)
wg2.add_straight_segment(length=75)
wg2.add_bend(-pi/2, radius=50)
wg2.add_straight_segment(length=10)
right_coupler = GratingCoupler.make_traditional_coupler_from_database_at_port(wg2.current_port, 'sn330', 1550)

cell = Cell('SIMPLE_DEVICE')
cell.add_to_layer(1, left_coupler, wg1, ring_res, wg2, right_coupler)

cell.show()

# cell.save('./layout/test.gds')
