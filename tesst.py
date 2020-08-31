from math import pi
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.resonator import RingResonator

coupler = GratingCoupler.make_traditional_coupler_from_database([0,0], 1, 'sn330', 1550)
coupler_shapely = coupler.get_shapely_object()

# Do the manipulation
buffered_coupler_shapely = coupler_shapely.buffer(2)
gg = buffered_coupler_shapely.difference(coupler_shapely)

cell = Cell('CELL')
cell.add_to_layer(1, buffered_coupler_shapely)
cell.add_to_layer(2, coupler_shapely)
cell.add_to_layer(3, gg)

cell.save('test.gds')