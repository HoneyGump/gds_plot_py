import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK_v1 as GC

lib = gdspy.GdsLibrary( precision=1e-10)

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

w_wg = 0.5
l_PortIn = 400
l_PortOut = l_PortIn
l_DC = 14
pos_y_heater = 150

gap = 0.2
radius_bend = 10
l_heater = 300
spacing_FA = 127
l_MZIs = l_heater*2 + 3*l_DC + 8*radius_bend
spacing_wg = 100
l_ver = pos_y_heater - radius_bend*2 - gap/2 - w_wg/2

# Geometry must be placed in cells.
DEVICES = lib.new_cell("MZMs_DC_L"+str(l_DC)+"_FA")

def build_DC(w, laayer=1, datatype=1):
    path_dc = gdspy.Path(w, (0,0))
    path_dc.segment(l_PortIn)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(spacing_FA/2-gap/2-w_wg/2-2*radius_bend)
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
    path_dc.segment(l_ver+spacing_wg)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_MZIs)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_ver+spacing_wg+gap/2+w_wg/2-spacing_FA*3/2)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_PortOut)

    return path_dc

def combine(w):
    DC = lib.new_cell('DC'+str(int(w*1000)))
    DC.add(build_DC(w))
    part1 = gdspy.CellReference(DC, origin=(0, -spacing_FA), rotation=0, x_reflection=True)
    part2 = gdspy.CellReference(DC)
    part = [part1, part2]
    return part

part1 = combine(w_wg)
part2 = combine(w_wg+6)
part = gdspy.boolean(part2, part1, 'xor', **ld_fulletch)
DEVICES.add(part)

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
DEVICES.add(gdspy.CellReference(cell, (x_heater1, pos_y_heater-spacing_FA/2)))
DEVICES.add(gdspy.CellReference(cell, (x_heater2, pos_y_heater-spacing_FA/2)))


# cell = GC.gc_PC_uniform(lib,filename0='UGC_', D=0.165, d=0.690, w_wg=0.5, w_gc=12)
# DEVICES.add(gdspy.CellArray(cell, 1, 4, (1, -spacing_FA), (0, spacing_FA)))
name_gds = "DC2_L"+str(l_DC)+".gds"
lib.write_gds(name_gds)
print(name_gds)
