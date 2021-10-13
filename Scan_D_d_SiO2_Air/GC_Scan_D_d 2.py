import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK as GC

w_wg = 0.5
w_etch = 3
w = 10

lib = gdspy.GdsLibrary( precision=1e-10)
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")

text = 'D 145'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, 50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.145, 0.665, n=(3,6))


text = 'D 160'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.160, 0.680, origin=posi_end, n=(3,6))

text = 'Apod 1'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for Air
filename = './data_apodized/apod_2D_params_Air_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, DEVICES, para, origin=posi_end, n=(3,6))

text = 'Apod 2'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for Air
dir_file = './data_apodized/Peorid_Diameter_min80_all.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180
d = temp['d_goal']*1e6 
posi_end = GC.Scan_d_Apod(lib, DEVICES, D2, d, origin=posi_end, n=(3,6))
posi_end = GC.Scan_D_Apod(lib, DEVICES, D2, d, origin=posi_end, n=(3,6))

lib.write_gds('test2.gds')