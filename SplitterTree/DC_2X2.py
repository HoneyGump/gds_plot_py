import sys
sys.path.append('D:\OneDrive - shanghaitech.edu.cn\Document_software\Grating\py_gds')
import gdspy
from gdspy.operation import offset
import numpy as np
import Photonics_PDK_v1 as GC

kwargs = {'w_gc': 12, 'w_wg': 0.510}

lib = gdspy.GdsLibrary( precision=1e-9)

# define the cell 
DEVICE = lib.new_cell('Die')

# define the splitter 1X2
len_bezier = 20
w_bezier = 10
gap = 0.2

w_wg = 0.5
w_wg_cld = 4.5
w_Al = 20
len_DC = 10
offset_y = gap/2 + w_wg/2 + w_bezier
len_mmi_22 = len_bezier*2 + len_DC
len_heater = 200
len_port_ext = 5
in_1_mmi_22 = gap/2 + w_wg/2 + w_bezier
in_2_mmi_22 = -in_1_mmi_22
out_1_mmi_22 = in_1_mmi_22
out_2_mmi_22 = -in_1_mmi_22

spacing_Al = w_Al + 2
layer_FETCH_COR = {'layer': 1, 'datatype':1}
layer_FETCH_CLD = {'layer': 31, 'datatype':2}
layer_M1 = {'layer': 3, 'datatype':1}
layer_DA = {'layer': 100, 'datatype':0}
layer_DETCH = {'layer': 64, 'datatype':0}
layer_fetch = {"layer": 1, "datatype": 1}
layer_heater = {"layer": 2, "datatype": 1}
layer_wire = {"layer": 3, "datatype": 1}
pos_y_heater = 127/2
radius= 10
len_Al_init = 10
len_EC = 523.9
w_EC = 342

def connect_zShape(cell, pos_start=(0,0),pos_end=(0,0), direction=1, w=w_wg, layer=1, datatype=1):
        '''
            pos_end is relative to the pos_start
        '''
        path = gdspy.Path(w, pos_start)
        path.segment(len_port_ext, layer=layer, datatype=datatype)
        if direction == 1:
            path.turn(radius, 'r', layer=layer, datatype=datatype)
        else:
            path.turn(radius, 'l', layer=layer, datatype=datatype)
        path.segment(abs(pos_end[1] - pos_start[1]) - 2*radius, layer=layer, datatype=datatype)
        if direction == 1:
            path.turn(radius, 'l', layer=layer, datatype=datatype)
        else:
            path.turn(radius, 'r', layer=layer, datatype=datatype)
        path.segment(pos_end[0] - 2*radius - len_port_ext, layer=layer, datatype=datatype)
        # cell.add(path)
        return path
    
def connect_zShape2(cell, pos_start=(0,0), pos_end=(0,0), direction=1):
    path1 = connect_zShape(cell, pos_start, pos_end, direction, w_wg, **layer_FETCH_COR)
    path2 = connect_zShape(cell, pos_start, pos_end, direction, w_wg_cld, **layer_FETCH_CLD)
    cell.add(gdspy.boolean(path2, path1, 'xor', **layer_fetch))

def connect_LShape(cell, pos_start=(0,0), pos_stop=(0,0)):
    x_ext = 30
    y_ext = 30
    # Path defined by a sequence of points and stored as a GDSII path
    if pos_stop[1] < pos_start[1]:
        sp1 = gdspy.FlexPath(
            [pos_start, (pos_stop[0], pos_start[1]), pos_stop, (pos_stop[0]-x_ext, pos_stop[1]), (pos_stop[0]-x_ext, pos_stop[1]-y_ext)], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
        )
    else:
        sp1 = gdspy.FlexPath(
            [pos_start, (pos_stop[0], pos_start[1]), pos_stop, (pos_stop[0]-x_ext, pos_stop[1]), (pos_stop[0]-x_ext, pos_stop[1]+y_ext)], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
        )
    cell.add(sp1)

def connect_lineShape(cell, pos_start, len):
        path = gdspy.Path(w_wg, pos_start)
        path.segment(len, **layer_FETCH_COR)
        cell.add(path)
        path = gdspy.Path(w_wg_cld, pos_start)
        path.segment(len, **layer_FETCH_CLD)
        cell.add(path)

def DC_2X2(w=0.5, gap=0.2, len_bezier=20, w_bezier=10, len_DC=len_DC):
    path1 = gdspy.Path(w, (0,0))
    path1.bezier([(len_bezier/2, 0), (len_bezier/2, -w_bezier), (len_bezier, -w_bezier)], tolerance=0.005, **layer_FETCH_COR)
    path1.segment(len_DC, **layer_FETCH_COR)
    path1.bezier([(len_bezier/2, 0), (len_bezier/2, w_bezier), (len_bezier, w_bezier)], tolerance=0.005, **layer_FETCH_COR)

    path2 = gdspy.Path(w, (0,-w_bezier*2-gap-w_wg))
    path2.bezier([(len_bezier/2, 0), (len_bezier/2, w_bezier), (len_bezier, w_bezier)], tolerance=0.005, **layer_FETCH_COR)
    path2.segment(len_DC, **layer_FETCH_COR)
    path2.bezier([(len_bezier/2, 0), (len_bezier/2, -w_bezier), (len_bezier, -w_bezier)], tolerance=0.005, **layer_FETCH_COR)

    return [path1, path2]

def Heater(l_heater2):
    # define  heater
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

    path1 = gdspy.Path(w_wg)
    path1.segment(l_heater2)
    path2 = gdspy.Path(w_wg_cld)
    path2.segment(l_heater2)
    cell.add(gdspy.boolean(path2, path1, 'xor', **layer_FETCH_COR))

    return cell

def Splitter_12():
    Splitter_1X2 = lib.new_cell('Splitter_1X2')
    DC = lib.new_cell('DC_2X2')
    heater = Heater(200)
    # define 2X2
    # DC_2X2
    
    part1 = DC_2X2(w_wg, gap, len_bezier, w_bezier)
    part2 = DC_2X2(w_wg_cld, gap, len_bezier, w_bezier)
    DC.add(gdspy.boolean(part2, part1, 'xor', **layer_FETCH_COR))
    ## MMI 2X2
    
    pos_x = 0 
    Splitter_1X2.add(gdspy.CellReference(DC, (pos_x, offset_y)))
    pos_x = len_mmi_22
    # # wg
    connect_zShape2(Splitter_1X2, (pos_x, out_1_mmi_22), (2*radius+len_port_ext*2, pos_y_heater), 0)
    connect_zShape2(Splitter_1X2, (pos_x, out_2_mmi_22), (2*radius+len_port_ext*2+len_heater, -pos_y_heater), 1)
    # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    ## add  1st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # wg 
    connect_zShape2(Splitter_1X2, (pos_x, pos_y_heater), (2*radius+len_port_ext*2, in_1_mmi_22), 1)
    connect_zShape2(Splitter_1X2, (pos_x, -pos_y_heater), (2*radius+len_port_ext*2, in_2_mmi_22), 0)
    # next
    pos_x += radius*2 + len_port_ext*2

    # ## the 2st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(DC, (pos_x, offset_y)))
    pos_x += len_mmi_22
    connect_zShape2(Splitter_1X2, (pos_x, out_1_mmi_22), (2*radius+len_port_ext*2, pos_y_heater), 0)
    connect_zShape2(Splitter_1X2, (pos_x, out_2_mmi_22), (2*radius+len_port_ext*2+len_heater, -pos_y_heater), 1)
    # # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    # ## add  2st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # # wg
    connect_zShape2(Splitter_1X2, (pos_x, pos_y_heater), (2*radius+len_port_ext*2, in_1_mmi_22), 1)
    connect_zShape2(Splitter_1X2, (pos_x, -pos_y_heater), (2*radius+len_port_ext*2, in_2_mmi_22), 0)
    # # # next
    pos_x += radius*2 + len_port_ext*2

    # # the 3st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(DC, (pos_x, offset_y)))

    # add commom GND
    x_1 = len_mmi_22 + len_heater + (radius+len_port_ext)*2 - 15
    len_GND = (radius+len_port_ext)*4 + len_mmi_22 + 31
    path = gdspy.FlexPath([(x_1, pos_y_heater), (x_1+len_GND, pos_y_heater)], w_Al, 0, gdsii_path=True, **layer_M1)
    Splitter_1X2.add(path)
    x_1 =len_mmi_22 + len_heater + (radius+len_port_ext)*4 + len_mmi_22/2
    path = gdspy.FlexPath([(x_1, pos_y_heater-80), (x_1, pos_y_heater+80)], 150, 0,  gdsii_path=True, **layer_M1)
    Splitter_1X2.add(path)

    return Splitter_1X2
    
def Splitter_tree2(num=16):
    Splitter_1X2 = Splitter_12()
    ## define the splitter tree
    pos_x = 0
    pos_y = 0
    pos_y_min = -(num-1)*pos_y_heater - 10
    pos_y_max = -pos_y_min + 10
    pos_x_pad1 = len_mmi_22 + 2*(radius + len_port_ext) + 10
    pos_x_pad2 = len_mmi_22 + len_mmi_22 + 2*len_heater + 6*(radius + len_port_ext) - 10
    len_splitter_1X2 = len_mmi_22 + 2*len_mmi_22 + 2*len_heater + 8*(radius + len_port_ext)
    default_gap = len_mmi_22 + 6*(radius + len_port_ext) + len_mmi_22 + 15
    space_y = 4*pos_y_heater
    space_x = len_splitter_1X2 + 2*(radius + len_port_ext)
    len_Al_init = 12

    N = int(np.floor(np.log2(num)))
    ST = lib.new_cell('Splitter_tree')
    
    for i in range(N):
        # number of wire
        temp_n = (2**(i-1)+2**(i-2))
        # offset for the position of splitter
        if spacing_Al*temp_n < default_gap:
            x_offset = 0
        else:
            x_offset = spacing_Al*temp_n - default_gap
        # extend length for waveguide
        if spacing_Al*temp_n*2 < default_gap:
            x_offset2 = 0
        else:
            x_offset2 = spacing_Al*temp_n*2 - default_gap
        # define the position
        if i == 0:
            pos_x = 0
        else:
            pos_x += space_x 
        pos_x += x_offset
        # the max length of wire in the x direction
        len_Al_max = (2**i/2-1)*spacing_Al + len_Al_init 
        # building the block
        for j in range(2**i):
            pos_y = (-(2**i-1)/2*2**(N-1-i) + 2**(N-1-i)*j) * space_y
            # place the splitter
            ST.add(gdspy.CellReference(Splitter_1X2, (pos_x, pos_y)))
            # add Al
            if j < 2**(i-1):
                connect_LShape(ST, (pos_x+pos_x_pad1, pos_y+pos_y_heater), (pos_x+pos_x_pad1-len_Al_init-j*spacing_Al, pos_y_min))
                connect_LShape(ST, (pos_x+pos_x_pad2, pos_y+pos_y_heater), (pos_x+pos_x_pad2+len_Al_init+j*spacing_Al, pos_y_min))
            else:
                connect_LShape(ST, (pos_x+pos_x_pad1, pos_y+pos_y_heater), (pos_x+pos_x_pad1-len_Al_max+(j-2**(i-1))*spacing_Al, pos_y_max))
                connect_LShape(ST, (pos_x+pos_x_pad2, pos_y+pos_y_heater), (pos_x+pos_x_pad2+len_Al_max-(j-2**(i-1))*spacing_Al, pos_y_max))
            # add wg
            if i == N-1:
                x_offset2 = 20
            if i < N:
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_22), (2*radius+len_port_ext*2+x_offset2, pos_y+2**(N-2-i)*space_y/2+offset_y), 0)
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_22), (2*radius+len_port_ext*2+x_offset2, pos_y-2**(N-2-i)*space_y/2+offset_y), 1)
    return ST

if __name__ == '__main__':
    
    st = Splitter_tree2(4)
    pos_x = st.get_bounding_box()[1][0]
    DEVICE.add(gdspy.CellReference(st))
    cell = GC.gc_PC_uniform(lib,filename0='UGC_', D=0.165, d=0.690, w_wg=0.5, w_gc=12, w_etch=2)
    DEVICE.add(gdspy.CellArray(cell, 1, 4, (1, -127), (pos_x, -127*3/2+offset_y), rotation=180))
    DEVICE.add(gdspy.CellReference(cell, (0, offset_y)))

    lib.write_gds('main.gds')

