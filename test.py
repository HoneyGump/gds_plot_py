import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

kwargs = {'w_gc': 12, 'w_wg': 0.517}

lib = gdspy.GdsLibrary( precision=1e-10)
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")

GC.gc_PC_uniform(lib,'GC_SiO2', a=0.23, D=0.165, d=0.71, period_num=29,w_gc=10, l_taper_a=500,l_grating=37)

lib.write_gds('test2.gds')