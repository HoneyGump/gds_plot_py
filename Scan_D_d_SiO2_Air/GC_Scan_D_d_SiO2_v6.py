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


posi_end = (0,0)
text = '1D 165'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.165, 0.715, '1UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = '1D 175'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.175, 0.725, '1UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = '1AGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
d = temp['d_goal']*1e6 
posi_end = GC.Scan_d_Apod(lib, GC_scan, D, d, '1AGC_SiO2', step=0.005, offset_scan=-0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_D_Apod(lib, GC_scan, D, d, '1AGC_SiO2', step=0.005, offset_scan=0, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs, D_max=0.18)

text = '1AGC R'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
filename = './data_apodized/apod_2D_params_SiO2_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, GC_scan, para, '1AGC_SiO2', step=0.005, offset_scan=0, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_tooth(lib, GC_scan, para, '1AGC_SiO2', step=0.005, offset_scan=0, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)
DEVICES = lib.new_cell("Devices")
#####################################################################################################################vvv
posi_end = (1300, 0)
text = '2D 160'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.160, 0.720, '2UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = '2D 170'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.170, 0.730, '2UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = '2AGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
d = temp['d_goal']*1e6 
posi_end = GC.Scan_d_Apod(lib, GC_scan, D-0.01, d, '2AGC_SiO2', step=0.005, offset_scan=-0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_D_Apod(lib, GC_scan, D-0.01, d, '2AGC_SiO2', step=0.005, offset_scan=0, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

text = '2AGC R'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
# load data for SiO2
filename = './data_apodized/apod_2D_params_SiO2_8Deg.txt'
para = GC.readParameters(filename)
posi_end = GC.Scan_trench(lib, GC_scan, para, '2AGC_SiO2', step=0.005, offset_scan=-0.02, origin=posi_end, n=(4,2), space=200, type_GC='FA', **kwargs)
posi_end = GC.Scan_tooth(lib, GC_scan, para, '2AGC_SiO2', step=0.005, offset_scan=0.03, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

#####################################################################################################################vvv
# line
posi_end = (2600, 0)

text = '3D 165'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.165, 0.720, '3UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)

text = '3D 175'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.175, 0.730, '3UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)

text = '3AGC P'
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
posi_end = GC.Scan_d_Apod(lib, GC_scan, D, d, '3AGC_SiO2', step=0.005, offset_scan=-0.005, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)
#####################################################################################################################vvv
# line
posi_end = (2600, -4800)

text = '4D 160'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.160, 0.720, '4UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)

text = '4D 170'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
GC_scan.add(ref)
posi_end = GC.Scan_d(lib, GC_scan, 0.170, 0.730, '4UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)

text = '4AGC P'
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
posi_end = GC.Scan_D_Apod(lib, GC_scan, D, d, '4AGC_SiO2', step=0.005, offset_scan=0, origin=posi_end, n=(3,3), space=200, type_GC='line', **kwargs)
##

posi_end = (1000, 0)
DEVICES.add(gdspy.CellArray(GC_scan, 1, 1, (7500, 0), posi_end))

# # load Wang Jin Yi
lib.read_gds('ring_phC_V3.gds',rename_template='L_{name}')
name_cell = 'L_Ring_PhC'
cell = lib.cells[name_cell]
posi_end = (6000, -500)
DEVICES.add(gdspy.CellArray(cell, 1, 2, (posi_end[0], -800), posi_end))
lib.precision = 1e-10

# MZMs
posi_end = (posi_end[0], -3000)
text = 'MZMs'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load the two gds file
lib2 = gdspy.GdsLibrary( precision=1e-10)
lib2.read_gds('DC2_L10.gds')
lib2.read_gds('DC2_L12.gds')
lib2.read_gds('DC2_L14.gds')

name_cell = 'MZMs_DC_L10_FA'
cell = lib.new_cell(name_cell)
cell.add(lib2.cells[name_cell])
name_cell = 'MZMs_DC_L12_FA'
cell = lib.new_cell(name_cell)
cell.add(lib2.cells[name_cell])
name_cell = 'MZMs_DC_L14_FA'
cell = lib.new_cell(name_cell)
cell.add(lib2.cells[name_cell])

cell_MZM = lib.new_cell('MZMs_')
cell_MZM.add(gdspy.CellReference(lib.cells["MZMs_DC_L10_FA"], (0, 0)))
cell_MZM.add(gdspy.CellReference(lib.cells["MZMs_DC_L12_FA"], (0, -700)))
cell_MZM.add(gdspy.CellReference(lib2.cells["MZMs_DC_L14_FA"], (0, -1400)))
# add GC_FA for MZMs
cell_GC = lib.cells['1AGC_SiO2_D0']
cell_MZM.add(gdspy.CellArray(cell_GC, 1, 4, (0,127), (0, -127*2)))
cell_MZM.add(gdspy.CellArray(cell_GC, 1, 4, (0,127), (0, -700-127*2)))
cell_MZM.add(gdspy.CellArray(cell_GC, 1, 4, (0,127), (0, -1400-127*2)))
DEVICES.add(gdspy.CellArray(cell_MZM, 1, 2, [0, -2000], (posi_end[0], posi_end[1] - 200)))

# add ring resonant
# cell = lib.new_cell('RING')
# test = GC.Ring_4port(1,1)
# lib.add(test.place_ring(2000))
# pitch = 2300
# cell.add(gdspy.CellArray(lib.cells['Ring'], 2, 1, (pitch, 0), rotation=-90))
# pos_port = test.port
# l = pos_port[3][0]
# w = -pos_port[3][1]
# radius = 10
# l_port = 50
# cell.add(gdspy.CellArray(cell_GC, 1, 4, (0, -127), (-l-radius-l_port, radius+127)))
# pos_x = -l-radius-l_port
# pos_y = radius+127
# pts = [(pos_x, pos_y), (0, pos_y), (0, 0)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# pos_y += -127
# pts = [(pos_x, pos_y), (-w, pos_y), (-w, 0)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# pos_y += -127
# pts = [(pos_x, pos_y), (pos_x+radius+l_port/2, pos_y), (pos_x+radius+l_port/2, -pitch-l-l_port/2),(-w, -pitch-l-l_port/2), (-w, -pitch-l)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# pos_y += -127
# pts = [(pos_x, pos_y), (pos_x+radius, pos_y), (pos_x+radius, -pitch-l-l_port),(0, -pitch-l-l_port), (0, -pitch-l)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# pts = [(-w, -l), (-w, -pitch)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# pts = [(0, -l), (0, -pitch)]
# path = GC.Path2WG(pts, 0.5,6.5,1,1)
# cell.add(path)
# posi_end = (posi_end[0], posi_end[1]-4500)
# DEVICES.add(gdspy.CellArray(cell, 2, 1, (3000, 0), (posi_end[0]+2000, posi_end[1])))

# posi_end = (posi_end[0]+2500, 0)
# # Splitter Tree
# text = 'S T'
# com = lib.new_cell(text)
# com.add(gdspy.Text(text, 40, (posi_end[0]+0, posi_end[1]+50), **ld_fulletch))
# ref = gdspy.CellReference(com)
# DEVICES.add(ref)
# # load the two gds file
# lib.read_gds('main.gds')
# DEVICES.add(gdspy.CellArray(lib.cells["Die"], 1, 2, [0, -800], (posi_end[0], posi_end[1] - 200)))

mark = GC.Mark_crossmark(lib, **layer_Mark)
ref = gdspy.CellArray(mark, 2, 2, [10000, -10000], (0, 0))
DEVICES.add(ref)
lib.write_gds('GC_MZM_SiO2_v6.gds')