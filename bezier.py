import numpy as np
import gdspy
import scipy.io as scio

# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)

# create a new cell to save all devices or all device
DEVICES = lib.new_cell("DEVICES")

# a common bezier curve 
def bc(w_wg = 0.5, l_bc = 100, w_bc = 127/2, tolerance = 0.01):
    ''' w_wg is the width of waveguide \n
        l_bc is length of bezier curve \n
        w_bc is the width of bezier curve'''
    path = gdspy.Path(w_wg, (0, 0))
    v = [(l_bc/2, 0), (l_bc/2, w_bc), (l_bc, w_bc)] # the first point (0, 0) is omiited
    path.bezier(v, tolerance = tolerance)
    return path

# bezier curve with is_inverted 
def bezierCurve(w_wg = 0.5, l_bc = 100, w_bc = 127/2, w_etch = 3, tolerance = 0.01, is_inverted = True):
    ''' w_wg is the width of waveguide \n
        l_bc is length of bezier curve \n
        w_bc is the width of bezier curve'''
    path1 = bc(w_wg)
    if is_inverted == True:
        path2 = bc(w_wg + w_etch*2)
        inverted = gdspy.boolean(path1, path2, 'xor')
        return inverted
    else:
        return path1

DEVICES.add(bezierCurve(1))
lib.write_gds('test_bc.gds')
gdspy.LayoutViewer()