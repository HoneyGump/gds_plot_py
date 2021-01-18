import numpy as np
import gdspy
import Photonics_PDK

w_wg = 0.5
l_wg = 300
w_gc = 10
w_etch = 3
l_taper_a = 500
l_gc_sphere = 100
# ring parameters
gap= 0.1
radius_ring = 10

lib = gdspy.GdsLibrary( precision=1e-10 )

# create grating
grating = Photonics_PDK.gratingCoupler_tradition(lib, a=0.23, D=0.150, d=0.665, period_num=29, w_gc=10, l_taper_a=500, l_grating=30, w_wg=0.5, w_etch=3 )

# create the cell: waveguide
wg = lib.new_cell('wg')
points = [(0, w_wg/2), (l_wg, w_wg/2), (l_wg, -w_wg/2), (0, -w_wg/2)]
poly = gdspy.Polygon(points)
Photonics_PDK.convert_to_positive_resist(wg, poly, buffer_radius=3)

# create the cell: grating region for sphere
gc_sphere = lib.new_cell('GCForSphere')
points = [(0, w_wg/2), (l_taper_a, w_gc/2), (l_taper_a+l_gc_sphere, w_gc/2), (l_taper_a*2+l_gc_sphere, w_wg/2), (l_taper_a*2+l_gc_sphere, -w_wg/2), (l_taper_a+l_gc_sphere, -w_gc/2), (l_taper_a, -w_gc/2), (0, -w_wg/2)]
poly = gdspy.Polygon(points)
Photonics_PDK.convert_to_positive_resist(gc_sphere, poly, buffer_radius=3)

# create ring 
ring = lib.new_cell('ring_R'+str(int(radius_ring))+'_gap'+str(int(gap*1000)))
points = [(0, -w_wg/2), (l_wg, -w_wg/2), (l_wg, w_wg/2), (0, w_wg/2)]
poly = gdspy.Polygon(points)
arc = gdspy.Round(
    (l_wg/2, -gap-w_wg-radius_ring),
    radius_ring+w_wg/2,
    inner_radius=radius_ring-w_wg/2 ,
    tolerance=0.001,
)
Photonics_PDK.convert_to_positive_resist(ring, [poly, arc], buffer_radius=3)

col = 1 
row = 5
devices = lib.new_cell('Devices')

# assemble w 500 nm
spacing = (0, -127)
origin = (0, 0)
devices.add(gdspy.CellArray(grating, col, row, (spacing [0], -spacing [1]), origin=origin, rotation=180))
devices.add(gdspy.CellArray(wg, col, row, spacing, origin=origin))
devices.add(gdspy.CellArray(grating, col, row, spacing , origin=(origin[0]+l_wg, origin[1]+0)))

# assemble w 10 um 
spacing = (0, -127)
origin = (1500, 0)
devices.add(gdspy.CellArray(grating, col, row, (spacing [0], -spacing [1]), origin=origin, rotation=180))
devices.add(gdspy.CellArray(gc_sphere, col, row, spacing, origin=origin))
devices.add(gdspy.CellArray(grating, col, row, spacing, origin=(origin[0]+l_taper_a*2+l_gc_sphere, origin[1]+0)))

# assemble ring
spacing = (0, -127)
origin = (4000, 0)
devices.add(gdspy.CellArray(grating, col, row, (spacing [0], -spacing [1]), origin=origin, rotation=180))
devices.add(gdspy.CellArray(ring, col, row, spacing, origin=origin))
devices.add(gdspy.CellArray(grating, col, row, spacing, origin=(origin[0]+l_wg, origin[1]+0)))


# Save the library in a file called 'first.gds'.
lib.write_gds('Grating_sphere_v2.gds')
gdspy.LayoutViewer()

