import numpy as np
import gdspy

layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 3}
ld_heater = {"layer": 2, "datatype": 1}
ld_wire = {"layer": 3, "datatype": 1}

info_wg = {"w_wg":0.5, "w_etch": 3}

# define direction coupler
def DC(lib, cellName='DC', l_Coupler=20, spacing=0.6, radius_bend=10, l_ver=10, w_wg=0.5):
    l_PortIn = 10
    cell = lib.new_cell(cellName)
    
    path_dc = gdspy.Path(w_wg, (0,0))
    path_dc.segment(l_PortIn)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_Coupler)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_PortIn)
    cell.add(path_dc)

    path_dc = gdspy.Path(w_wg, (0, -(l_ver*2+radius_bend*4+spacing)))
    path_dc.segment(l_PortIn)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_Coupler)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_PortIn)
    cell.add(path_dc)

    return cell

# define direction coupler2
def DC2(lib, cellName='DC', l_Coupler=20, spacing=0.6, radius_bend=10, l_ver=10, w_wg=0.5, w_etch=3 ):
    cell1 = DC(lib, 'temp1_'+cellName, l_Coupler, spacing, radius_bend, l_ver, w_wg)
    cell2 = DC(lib, 'temp2_'+cellName, l_Coupler, spacing, radius_bend, l_ver, w_wg+2*w_etch)
    lib.remove(cell1)
    lib.remove(cell2)
    cell = lib.new_cell(cellName)
    poly = gdspy.boolean(cell1, cell2, 'xor', **ld_fulletch)
    cell.add(poly)
    return cell

lib = gdspy.GdsLibrary( precision=1e-10)
DC2(lib)
# gdspy.LayoutViewer()
name_gds = "test_DC.gds"
lib.write_gds(name_gds)
print(name_gds)
