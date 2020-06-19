import numpy as np
import gdspy
import scipy.io as scio


# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)

# create a new cell to save all devices or all device
DEVICES = lib.new_cell("DEVICES")

# load the two gds file
lib.read_gds('./ApodizedGC.gds')
lib.read_gds('./UniformGC.gds')

# get the all cell name 
cell_all = lib.cells
# do the reference or copy operation
ref = gdspy.CellReference(cell_all['Devices'], (0,0))
ref2 = gdspy.CellReference(cell_all['Devices2'], (0,-3200))
DEVICES.add([ref, ref2])

# add the Text of the pair of letter and number
# for a easy identification
ld_fulletch = {"layer": 1, "datatype": 1}
# num is the text of column
# letter is the text of raw
num = '1234' 
letter = 'ABCDE'
# (x0, y0) is the origin of 'A1', A is the raw, 1 is the column
x0 = -600 
y0 = 50
# (x_steo, y_step) is the next Text's postion, eg 'A2'
x_step = 1500 
y_step = -800
for i in range(len(letter)):
    for j in range(len(num)):
        text = letter[i] + num[j]
        com = lib.new_cell(text)
        com.add(gdspy.Text(text, 40, (x0 + j*x_step, y0 + i*y_step), **ld_fulletch))
        ref = gdspy.CellReference(com)
        DEVICES.add(ref)

num = '1234' 
letter = 'F'
# (x0, y0) is the origin of 'A1', A is the raw, 1 is the column
x0 = -600 
y0 = -3750
# (x_steo, y_step) is the next Text's postion, eg 'A2'
x_step = 1500 
y_step = -800
for i in range(len(letter)):
    for j in range(len(num)):
        text = letter[i] + num[j]
        com = lib.new_cell(text)
        com.add(gdspy.Text(text, 40, (x0 + j*x_step, y0 + i*y_step), **ld_fulletch))
        ref = gdspy.CellReference(com)
        DEVICES.add(ref)


# save as gds format
lib.write_gds('Combinenation_SiO2.gds')
# gdspy.LayoutViewer()
