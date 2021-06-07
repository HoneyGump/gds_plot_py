import numpy as np
import gdspy
import scipy.io as scio

lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("devices")

# add the Text of the pair of letter and number
# for a easy identification
ld_fulletch = {"layer": 1, "datatype": 1}

text = 'ShanghaiTech'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 16))
ref = gdspy.CellReference(com)
DEVICES.add(ref)
        
lib.write_gds('Text_ShanghaiTech.gds')
gdspy.LayoutViewer()