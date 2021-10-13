import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

kwargs = {'w_gc': 12, 'w_wg': 0.510}

lib = gdspy.GdsLibrary( precision=1e-10)
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")

mark = GC.Mark_crossmark(lib)
ref = gdspy.CellArray(mark, 2, 2, [5000, -5500], (-500, 500))
DEVICES.add(ref)

text = 'D 165'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, 50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.165, 0.690, 'UGC_SiO2_', n=(3,3), **kwargs)


text = 'D 175'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.175, 0.705, 'UGC_SiO2_', origin=posi_end, n=(3,3), **kwargs)

text = 'AGC R'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for SiO2
filename = './data_apodized/apod_2D_params_SiO2_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, DEVICES, para, 'AGC_SiO2_', origin=posi_end, n=(4,2), **kwargs)
posi_end = GC.Scan_tooth(lib, DEVICES, para, 'AGC_SiO2_', origin=posi_end, n=(3,3), **kwargs)

text = 'AGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
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
posi_end = GC.Scan_d_Apod(lib, DEVICES, D2, d-0.020, 'AGC_SiO2_', origin=posi_end, n=(3,3), **kwargs)
posi_end = GC.Scan_D_Apod(lib, DEVICES, D2+0.015, d, 'AGC_SiO2_', origin=posi_end, n=(3,3), **kwargs)


# Testing Cell
posi_end = (0, 0)
Testing = lib.new_cell('Test_Stru')
cell = GC.gc_PC_uniform(lib,filename0='UGC_Air', D=0.145, d=0.665, w_wg=0.5, w_gc=12)
GC_line = GC.gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=0.5, w_gc=12) 
Testing.add(gdspy.CellReference(GC_line, posi_end))

posi_end = ((posi_end[0], posi_end[1]-100))
cell = GC.gc_PC_uniform(lib,filename0='UGC_Air', D=0.160, d=0.680, w_wg=0.5, w_gc=12)
GC_line = GC.gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=0.5, w_gc=12) 
Testing.add(gdspy.CellReference(GC_line, posi_end))

filename = './data_apodized/apod_2D_params_Air_8Deg.txt'
posi_end = ((posi_end[0], posi_end[1]-100))
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, Testing, para, origin=posi_end, n=(3,-2), **kwargs)

posi_end = ((posi_end[0], posi_end[1]+100))
dir_file = './data_apodized/Peorid_Diameter_min80_all.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180
d = temp['d_goal']*1e6 
posi_end = GC.Scan_D_Apod(lib, Testing, D2+0.015, d, origin=posi_end, n=(0,1), **kwargs)


posi_end = (1500, 0)
text = 'Testing'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
DEVICES.add(gdspy.CellArray(Testing, 1, 2, [0, -800], origin=posi_end))
# load the two gds file
lib.read_gds('DC.gds')

DEVICES.add(gdspy.CellArray(lib.cells["DC_MZMs"], 1, 4, [0, -800], (1500, -1600)))


lib.write_gds('test2.gds')