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

text = 'D 145'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, 50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.145, 0.665, n=(3,3), **kwargs)


text = 'D 160'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.160, 0.680, origin=posi_end, n=(3,3), **kwargs)

text = 'Apod 1'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for Air
filename = './data_apodized/apod_2D_params_Air_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, DEVICES, para, origin=posi_end, n=(4,2), **kwargs)
posi_end = GC.Scan_tooth(lib, DEVICES, para, origin=posi_end, n=(3,3), **kwargs)

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
posi_end = GC.Scan_d_Apod(lib, DEVICES, D2, d-0.035, origin=posi_end, n=(3,3), **kwargs)
posi_end = GC.Scan_D_Apod(lib, DEVICES, D2+0.02, d, origin=posi_end, n=(3,3), **kwargs)


posi_end = (1500, 0)
text = 'D 150'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.150, 0.670, origin=posi_end, n=(3,3), **kwargs)

text = 'D 155'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.155, 0.675, origin=posi_end, n=(3,3), **kwargs)

text = 'focu 1'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for Air
filename = './data_apodized/apod_2D_params_Air_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_ltaper_focu(lib, DEVICES, l_taper=12, para=para, origin=posi_end, n=(3,3), **kwargs)

text = 'focu 2'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
para = np.array(para)
temp_para = np.array(para)
for index_para in range(len(para)):
    if index_para % 2 != 0:
        temp_para[index_para] = para[index_para] + 0.02
temp_para = list(temp_para)
posi_end = GC.Scan_ltaper_focu(lib, DEVICES, l_taper=10, cellname_prefix='GC_focusing_d20_',para=temp_para, origin=posi_end, n=(3,3), **kwargs)

text = 'focu 3'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
para = np.array(para)
temp_para = np.array(para)
for index_para in range(len(para)):
    if index_para % 2 != 0:
        temp_para[index_para] = para[index_para] + 0.03
temp_para = list(temp_para)
posi_end = GC.Scan_ltaper_focu(lib, DEVICES, l_taper=14, cellname_prefix='GC_focusing_d30_',para=temp_para, origin=posi_end, n=(3,3), **kwargs)

text = 'focu 4'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
para = np.array(para)
temp_para = np.array(para)
for index_para in range(len(para)):
    if index_para % 2 == 0:
        temp_para[index_para] = para[index_para] - 0.017
temp_para = list(temp_para)
posi_end = GC.Scan_ltaper_focu(lib, DEVICES, l_taper=14, cellname_prefix='GC_focusing_D-17_',para=temp_para, origin=posi_end, n=(3,3), **kwargs)

# load the two gds file
lib.read_gds('DC.gds')

# DEVICES.add(gdspy.CellReference())

lib.write_gds('test2.gds')