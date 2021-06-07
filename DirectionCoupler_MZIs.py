import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DC_MZMs")

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

w_wg = 0.5
l_PortIn = 100
l_PortOut = l_PortIn
l_DC = 10
l_ver = 300
gap = 0.2
radius_bend = 10
l_heater = 300

path_dc = gdspy.Path(w_wg, (0,0))
path_dc.segment(l_PortIn)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_DC)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_heater)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_DC)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_heater)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_DC)
path_dc.turn(radius_bend,'l')
path_dc.segment(l_ver)
path_dc.turn(radius_bend,'r')
path_dc.segment(l_PortOut)

path_dc2 = gdspy.Path(w_wg, (0,0-l_ver*2-w_wg-gap-4*radius_bend))
path_dc2.segment(l_PortIn)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_DC)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_heater)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_DC)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_heater)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_DC)
path_dc2.turn(radius_bend,'r')
path_dc2.segment(l_ver)
path_dc2.turn(radius_bend,'l')
path_dc2.segment(l_PortOut)


path_dc_buffer = gdspy.offset([path_dc, path_dc2], 3, join_first=True)
path_positive = gdspy.boolean(path_dc_buffer, [path_dc, path_dc2], 'xor')

x0 = 0
point = [(x0, 20), (x0-20, 20), (x0-20, -1000), (x0, -1000)]
poly1 = gdspy.Polygon(point)
x0 = l_heater*2+12*radius_bend+l_PortIn+l_PortOut+3*l_DC+20
point = [(x0, 20), (x0-20, 20), (x0-20, -1000), (x0, -1000)]
poly2 = gdspy.Polygon(point)

path_positive = gdspy.boolean(path_positive, [poly1, poly2], 'not', layer=1, datatype=1)

DC = lib.new_cell("DC")
DC.add(path_positive)


# define  heater
layer_heater = {"layer": 2, "datatype": 1}
layer_wire = {"layer": 3, "datatype": 1}
l_heater2 = l_heater - 100
w_heater = 3
w_port = 10
w_wire = w_port*2
cell = lib.new_cell('heater')
# add middle long rect
heater = gdspy.Rectangle((0, w_heater/2), (l_heater2, -w_heater/2), **layer_heater)
cell.add(heater)
# add left rect and wire
heater = gdspy.Rectangle((-w_port/2, w_port/2), (w_port/2, -w_port/2), **layer_heater)
cell.add(heater)
heater = gdspy.Rectangle((-w_wire/2, w_wire/2), (w_wire/2, -w_wire/2), **layer_wire)
cell.add(heater)
# add right rect and wire
heater = gdspy.Rectangle((l_heater2-w_port/2, w_port/2), (l_heater2+w_port/2, -w_port/2), **layer_heater)
cell.add(heater)
heater = gdspy.Rectangle((l_heater2-w_wire/2, w_wire/2), (l_heater2+w_wire/2, -w_wire/2), **layer_wire)
cell.add(heater)

# add heater
x_heater1 = l_PortIn+4*radius_bend+l_DC+50
x_heater2 = l_PortIn+8*radius_bend+l_DC*2+l_heater+50
DC.add(gdspy.CellReference(cell, (x_heater1, 0)))
DC.add(gdspy.CellReference(cell, (x_heater2, 0)))

DEVICES.add(gdspy.CellReference(DC, (0,0)))

h_dc = l_ver*2 + radius_bend*4 + gap + w_wg
l_dc = l_DC*3 + l_PortIn + l_PortOut + l_heater*2 + radius_bend*12
cell = GC.gc_PC_uniform(lib,filename0='UGC_', D=0.165, d=0.690, w_wg=0.5, w_gc=12)
DEVICES.add(gdspy.CellReference(cell, (0, 0)))
DEVICES.add(gdspy.CellReference(cell, (0, -h_dc)))
DEVICES.add(gdspy.CellReference(cell, (l_dc, 0), rotation=180))
DEVICES.add(gdspy.CellReference(cell, (l_dc, -h_dc), rotation=180))

lib.write_gds("DC.gds")
