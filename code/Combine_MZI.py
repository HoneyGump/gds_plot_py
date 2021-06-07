import numpy as np
import gdspy
import scipy.io as scio


# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)
# load the two gds file
lib.read_gds('./layout/IL_MZI.gds')
lib.read_gds('./layout/GC_NoSiO2.gds')
# get the all cell name 
cell_all = lib.cells


lib2 = gdspy.GdsLibrary(precision = 1e-10)
# create a new cell to save all devices or all device
GC = lib2.new_cell("GC_a230_D150_d665")
elements = cell_all['GC_a230_D150_d665']
GC.add(elements.flatten() )

Body = lib2.new_cell("Body")
elements = cell_all['MZI_']
Body.add(elements)

# do the reference or copy operation
device = lib2.new_cell("device")
ref2 = gdspy.CellReference(Body)
device.add(ref2)

ref = gdspy.CellReference(GC,origin=(-506, 0), rotation=180 )
device.add(ref)
ref = gdspy.CellReference(GC,origin=(1252.74+506, 0 ), rotation=0 )
device.add(ref)

ref = gdspy.CellReference(GC,origin=(-506, -150), rotation=180 )
device.add(ref)
ref = gdspy.CellReference(GC,origin=(1252.74+506, -150), rotation=0 )
device.add(ref)
# add the Text of the pair of letter and number
# for a easy identification
# ld_fulletch = {"layer": 1, "datatype": 1}

# save as gds format
lib2.write_gds('./layout/IL_MZI_NoSiO2.gds')
# gdspy.LayoutViewer()
