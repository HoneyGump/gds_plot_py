import numpy as np
import gdspy
import scipy.io as scio

lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("devices")

# add the Text of the pair of letter and number
# for a easy identification
ld_fulletch = {"layer": 1, "datatype": 1}
# num is the text of column
# letter is the text of raw
num = '123456789' 
letter = 'ABCDEFGHI'
# (x0, y0) is the origin of 'A1', A is the raw, 1 is the column
x0 = 0
y0 = 0
# (x_steo, y_step) is the next Text's postion, eg 'A2'
x_step = 100 
y_step = -100
for i in range(len(letter)):
    for j in range(len(num)):
        text = letter[i] + num[j]
        com = lib.new_cell(text)
        com.add(gdspy.Text(text, 40, (x0 + j*x_step, y0 + i*y_step), **ld_fulletch))
        ref = gdspy.CellReference(com)
        DEVICES.add(ref)
        
lib.write_gds('Letters_Num.gds')
gdspy.LayoutViewer()