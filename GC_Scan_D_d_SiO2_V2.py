import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

lib = gdspy.GdsLibrary( precision=1e-10)
# Geometry must be placed in cells.
GC_scan = lib.new_cell("GC_scan")

kwargs = {'w_gc': 12, 'w_wg': 0.510}
layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

posi_end = (0, 0)
text = 'D 165'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0], posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.165, 0.690, 'UGC_SiO2_', origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = 'D 175'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.175, 0.705, 'UGC_SiO2_', origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = 'AGC R'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
filename = './data_apodized/apod_2D_params_SiO2_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, GC_scan, para, 'AGC_SiO2_', origin=posi_end, n=(4,2), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_tooth(lib, GC_scan, para, 'AGC_SiO2_', origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = 'AGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180
d = temp['d_goal']*1e6 
posi_end = GC.Scan_d_Apod(lib, GC_scan, D2, d-0.020, 'AGC_SiO2_', origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_D_Apod(lib, GC_scan, D2+0.015, d, 'AGC_SiO2_', origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

##
posi_end = (2000, 0)
DEVICES = lib.new_cell("Devices")
DEVICES.add(gdspy.CellArray(GC_scan, 2, 1, (6000, 0), posi_end))

# MZMs
posi_end = (posi_end[0]+2000, 0)
text = 'MZMs'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load the two gds file
lib.read_gds('DC2.gds')
DEVICES.add(gdspy.CellArray(lib.cells["MZMs_DC_FA"], 1, 4, [0, -800], (posi_end[0], posi_end[1] - 200)))

posi_end = (posi_end[0], posi_end[1]-3400)
# Splitter Tree
text = 'S T'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load the two gds file
lib.read_gds('main.gds')

DEVICES.add(gdspy.CellArray(lib.cells["Die"], 1, 2, [0, -800], (posi_end[0], posi_end[1] - 200)))

mark = GC.Mark_crossmark(lib, **layer_Mark)
ref = gdspy.CellArray(mark, 2, 2, [10000, -10000], (0, 0))
DEVICES.add(ref)
lib.write_gds('GC_MZM_SiO2_v2.gds')