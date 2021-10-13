import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

lib = gdspy.GdsLibrary( precision=1e-10)

kwargs = {'w_gc': 12, 'w_wg': 0.510}
layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}

# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
d = temp['d_goal']*1e6 
GC.gc_PC_apodized(lib, 'AGC_SiO2_H220_a230_D-10', D-0.01, d)

# gdspy.LayoutViewer()
lib.write_gds('AGC_SiO2_H220_a230_D-10.gds')