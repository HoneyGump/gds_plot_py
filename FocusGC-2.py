import numpy as np
import gdspy

# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)

# create a new cell to save 
gc = lib.new_cell("GC")
ground = lib.new_cell("ground")
tooth = lib.new_cell("tooth")

# define the index of layer
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 2, "datatype": 1}

##################################################################
#         parameters setting
##################################################################
xp = 32 # xp is the length of first tooth
xp2 = 29.84 + 33 # xp2 is the length of end fanshshape

w_etch = 70 # width of etch
h_etch = 60 # hight of etch

l_wg = 2 # the length of straight waveguide
w_wg = 0.44 # the width of waveguide

a =  0.29 # width of etched tooth
b =  0.350 # width of remain tooth

GC_theta = 10/180*np.pi

period = 30
##################################################################

# create the rect region
points = [(w_etch, -h_etch/2), (w_etch, h_etch/2), (-l_wg/2, h_etch/2), (-l_wg/2, -h_etch/2)]
rect = gdspy.Polygon(points, **ld_fulletch)

# create the straight waveguide
points = [(l_wg/2, -w_wg/2), (l_wg/2, w_wg/2), (-l_wg/2, w_wg/2), (-l_wg/2, -w_wg/2)]
wg = gdspy.Polygon(points, **ld_fulletch)
# create the fanshape
arc = gdspy.Round(
        (0, 0),
        xp2,
        inner_radius=0,
        initial_angle= -GC_theta,
        final_angle= GC_theta,
        number_of_points=128,
        **ld_fulletch
    )
gd = gdspy.boolean(wg, arc, 'or', precision=1e-10, max_points=199, layer=1, datatype=1)
ground.add(gd)

# create the tooth
i=0
while i < period:
    arc = gdspy.Round(
        (0, 0),
        xp+a,
        inner_radius=xp,
        initial_angle= -GC_theta,
        final_angle= GC_theta,
        number_of_points=128,
        **ld_grating
    )
    tooth.add(arc)
    pitch = a + b   
    xp += pitch
    i += 1

inv = gdspy.boolean(gd, rect, 'xor', precision=1e-10, max_points=199, layer=0, datatype=1)
inv = gdspy.boolean(inv, tooth, 'or', precision=1e-10, max_points=199, layer=0, datatype=1)
gc.add(inv)
gc.add(gd)
gc.add(tooth)

lib.write_gds('FocusGC-2.gds')
gdspy.LayoutViewer()