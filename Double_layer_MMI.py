import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

kwargs = {'w_gc': 12, 'w_wg': 0.510}
layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}
ld_wire = {"layer": 3, "datatype": 1}

# add double layer MMI
lib = gdspy.GdsLibrary( precision=1e-10)
lib = lib.read_gds("Double_layer_MMI.GDS", layers={'8':1,'9':2}, datatypes={'0':0})
DEVICES = lib.new_cell('Device')
DEVICES.add(gdspy.CellArray(lib.cells['TOP'], 2, 1, (4500, -2500), (-4700, 1650-4000)))

# add UGC
posi_end = (800, -800)
text = '1D 165'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = GC.Scan_d(lib, DEVICES, 0.165, 0.715, '1UGC_SiO2', step=0.005, origin=posi_end, n=(3,3), space=200, type_GC='FA', **kwargs)

# add AGC P
text = '1AGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
d = temp['d_goal']*1e6 
cell = GC.gc_PC_apodized(lib, 'AGC_SiO2_H220_a230_d10', D, d+0.01, **kwargs)
GC_line = GC.gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=0.51)
DEVICES.add(gdspy.CellArray(GC_line, 2, 1, (1500, 0),  (posi_end[0], posi_end[1])))
posi_end = (posi_end[0], posi_end[1]-200)
cell = GC.gc_PC_apodized(lib, 'AGC_SiO2_H220_a230_d10_W10', D, d+0.01, w_gc=10, w_wg=0.51)
GC_line = GC.gc_line(lib.new_cell(cell.name+"_line"), cell, origin=(0,0), w_wg=0.51)
DEVICES.add(gdspy.CellArray(GC_line, 2, 1, (1500, 0), posi_end))

cell = GC.gc_PC_apodized(lib, 'AGC_SiO2_H220_a230_D-10', D-0.01, d, **kwargs)
posi_end = (posi_end[0], posi_end[1]-200)
GC_line = GC.gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=0.51)
DEVICES.add(gdspy.CellArray(GC_line, 2, 1, (1500, 0), posi_end))
posi_end = (posi_end[0], posi_end[1]-200)
cell = GC.gc_PC_apodized(lib, 'AGC_SiO2_H220_a230_D-10_W10', D-0.01, d, w_gc=10, w_wg=0.51)
GC_line = GC.gc_line(lib.new_cell(cell.name+"_line"), cell, origin=(0,0), w_wg=0.51)
DEVICES.add(gdspy.CellArray(GC_line, 2, 1, (1500, 0), posi_end))

# add FUGC
posi_end = (1500+800, -800)
text = '1FUGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = (1500+800-500, -800)
posi_end = GC.Scan_ltaper_UFocu(lib, DEVICES, 0.165, 0.715, 10, 'FUGC_PC', step=1, n=(2,5), origin=posi_end, space=200, type_GC='FA', **kwargs)

# add FAGC
posi_end = (1500+800+1500, -800)
text = '1FAGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = (1500+800+1500-500, -800)
D = np.reshape(D, -1)
d = np.reshape(d, -1)
posi_end = GC.Scan_ltaper_AFocu(lib, DEVICES, D-0.01, d, 10, 'FAGC_PC_D-10', step=1, n=(2,5), origin=posi_end, space=200, type_GC='FA', **kwargs)

# add FAGC
posi_end = (1500+800+1500*2, -800)
text = '2FAGC P'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (posi_end[0]+100, posi_end[1]+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
posi_end = (1500+800+1500*2-500, -800)
D = np.reshape(D, -1)
d = np.reshape(d, -1)
posi_end = GC.Scan_ltaper_AFocu(lib, DEVICES, D, d+0.01, 10, 'FAGC_PC_d10', step=1, n=(2,5), origin=posi_end, space=200, type_GC='FA', **kwargs)

# add mark
mark = GC.Mark_crossmark(lib, **layer_Mark)
ref = gdspy.CellArray(mark, 2, 2, [10000, -10000], (0, 0))
# add more mark
DEVICES.add(ref)
ref = gdspy.CellReference(mark, (-400, 0))
DEVICES.add(ref)
ref = gdspy.CellReference(mark, (10400, -10000))
DEVICES.add(ref)

w_pad = 300
l_pad = 450
# add pad
PAD = lib.new_cell('PAD')
PAD.add(gdspy.Rectangle((-w_pad/2, l_pad), (w_pad/2, 0), **ld_wire))

DEVICES.add(gdspy.CellArray(PAD, 40, 1, (400, 0), (-3000, 500)))

lib.write_gds('test.gds')
# gdspy.LayoutViewer()
