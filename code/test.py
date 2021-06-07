import numpy as np
import gdspy
import scipy.io as scio

lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")
cell = DEVICES
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

# parameter 1
ff = 0.616
num_pitch = 30
pitch = 0.8
w_wg = 0.5
w_etch = 3
xp = 12
GC_theta = 23/180*np.pi
GC_theta2 = 20/180*np.pi

pa = [0]*num_pitch*2
for i in range(num_pitch):
    pa[2*i] = round(pitch*(1-ff), 3)
    pa[2*i+1] = round(pitch*ff, 3)
i = 0
while i<len(pa):
    a =  float(pa[i])
    b =  float(pa[i+1])
    arc = gdspy.Round(
        (0, 0),
        xp+a,
        inner_radius=xp,
        initial_angle= -GC_theta+np.pi,
        final_angle= GC_theta+np.pi,
        number_of_points=128,
        **ld_grating
    )
    cell.add(arc)

    pitch = a + b   
    xp += pitch
    i += 2

GC_theta = GC_theta2
points = [(0, w_wg/2), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta)), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta) + w_etch), (0, w_wg/2 + w_etch)]
poly = gdspy.Polygon(points, **ld_fulletch)
cell.add(poly)

poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
cell.add(poly)

lib.write_gds('test.gds')
