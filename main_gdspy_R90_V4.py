import gdspy
from gdspy.operation import offset
import numpy as np
from numpy.core.defchararray import decode

kwargs = {'w_gc': 12, 'w_wg': 0.510}

lib = gdspy.GdsLibrary( precision=1e-9)

# lib.read_gds('GC_TE_1550.gds')
lib.read_gds('M1X2_TE_1550.gds')
lib.read_gds('M2X2_TE_1550.gds')
lib.read_gds('MH_TE_1550.gds')
lib.read_gds('BP.gds')
lib.read_gds('EC_1550.gds')
lib.read_gds('PBS_1550.gds')
lib.read_gds('GC_TM_1550.gds')
lib.read_gds('GC_TE_1550.gds')
# define the cell 
DEVICE = lib.new_cell('Die')

# define the splitter 1X2
len_mmi_12 = 12
len_mmi_22 = 125.4
len_heater = 410
len_port_ext = 3
out_1_mmi_12 = 0.775
out_2_mmi_12 = -0.775
in_1_mmi_22 = 1.5
in_2_mmi_22 = -1.5
out_1_mmi_22 = 1.5
out_2_mmi_22 = -1.5
w_wg = 0.45
w_wg_cld = 4.45
w_Al = 10
spacing_Al = w_Al + 2
layer_FETCH_COR = {'layer': 31, 'datatype':1}
layer_FETCH_CLD = {'layer': 31, 'datatype':2}
layer_M1 = {'layer': 11, 'datatype':1}
layer_DA = {'layer': 100, 'datatype':0}
layer_DETCH = {'layer': 64, 'datatype':0}
layer_PASS= {'layer': 60, 'datatype':0}
layer_ISL= {'layer': 67, 'datatype':0}
pos_y_heater = 60
radius= 20
len_Al_init = 12
len_EC = 523.9
w_EC = 342
pos_x_pad1 = len_mmi_12 + 2*(radius + len_port_ext) + 10.4
pos_x_pad2 = len_mmi_12 + len_mmi_22 + 2*len_heater + 6*(radius + len_port_ext) - 9.6
spacing_pad_x = 120
spacing_pad_y = 100
w_pad = 60
l_pad = 80
w_GND = 120
l_heater = 390
len_splitter_1X2 = len_mmi_12 + 2*len_mmi_22 + 2*len_heater + 8*(radius + len_port_ext)
spacing_splitter = len_splitter_1X2 + 2*len_port_ext + 2*radius
w_detch = 4.4
r_max = 8.1
r_min = 6.5


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
        cell.add(path)
    
def connect_zShape2(cell, pos_start=(0,0), pos_end=(0,0), direction=1):
    connect_zShape(cell, pos_start, pos_end, direction, w_wg, **layer_FETCH_COR)
    connect_zShape(cell, pos_start, pos_end, direction, w_wg_cld, **layer_FETCH_CLD)

def connect_zShape3(cell, w, len_port, pos_start, pos_end, layer, datatype):
    # Path defined by a sequence of points and stored as a GDSII path
    sp1 = gdspy.FlexPath(
            [pos_start, (pos_start[0]+len_port+radius, pos_start[1]), (pos_start[0]+len_port+radius, pos_end[1]), pos_end], w, 0, ends="flush",
             layer=layer, datatype=datatype, bend_radius=radius, corners='circular bend', tolerance=0.001
    )
    cell.add(sp1)

def connect_zShape4(cell, w, len_port, pos_start, pos_end):
    connect_zShape3(cell, w, len_port, pos_start, pos_end, **layer_FETCH_COR)
    connect_zShape3(cell, 4.45, len_port, pos_start, pos_end, **layer_FETCH_CLD)

def connect_LShape(cell, pos_start=(0,0), pos_middle=(0,0), pos_stop=(0,0)):
    x_ext = 30
    y_ext = 30
    # Path defined by a sequence of points and stored as a GDSII path
    sp1 = gdspy.FlexPath(
            [pos_start, (pos_middle[0], pos_start[1]), pos_middle, (pos_stop[0], pos_middle[1]), pos_stop], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
    )
    cell.add(sp1)

def connect_LShape_N90(cell, pos_start=(0,0), pos_stop=(0,0)):
    x_ext = 30
    y_ext = 30
    # Path defined by a sequence of points and stored as a GDSII path
    sp1 = gdspy.FlexPath(
            [pos_start, (pos_stop[0], pos_start[1]), pos_stop], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
    )
    cell.add(sp1)

def connect_NShape(cell, pos_start=(0,0),len_y1 = 10, len_x=200, len_y2=150, pos_stop_x=400):
    # Path defined by a sequence of points and stored as a GDSII path
    sp1 = gdspy.FlexPath(
            [pos_start, (pos_start[0], pos_start[1]+len_y1), (pos_start[0]+len_x, pos_start[1]+len_y1), (pos_start[0]+len_x, pos_start[1]+len_y1-len_y2), (pos_stop_x, pos_start[1]+len_y1-len_y2)], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
    )
    cell.add(sp1)

def connect_1Shape(cell, pos_start=(0,0), stop_x=400):
    # Path defined by a sequence of points and stored as a GDSII path
    sp1 = gdspy.FlexPath(
            [pos_start, (stop_x, pos_start[1])], w_Al, 0, gdsii_path=True, ends="flush", **layer_M1
    )
    cell.add(sp1)

def connect_lineShape(cell, pos_start=(0,0), len=100, direct='+x'):
        path = gdspy.Path(w_wg, pos_start)
        path.segment(len, direction=direct, **layer_FETCH_COR)
        cell.add(path)
        path = gdspy.Path(w_wg_cld, pos_start)
        path.segment(len, direction=direct, **layer_FETCH_CLD)
        cell.add(path)

def ISL_curve(center, radius, w, initial_angle, final_angle, offset=5):
    angle_ext_min = 10.5
    angle_ext_max = 6
    path1 = gdspy.Round(center, radius+w/2, radius-w/2, initial_angle=initial_angle/180*np.pi, final_angle=final_angle/180*np.pi, **layer_ISL, tolerance=0.001)
    if radius > 20:
        path2 = gdspy.Round(center, radius+w/2+1.1, radius-w/2-1.1, initial_angle=(initial_angle-angle_ext_max)/180*np.pi, final_angle=(final_angle+angle_ext_max)/180*np.pi, **layer_FETCH_CLD, tolerance=0.001)
    else:
        path2 = gdspy.Round(center, radius+w/2+1.1, radius-w/2-1.1, initial_angle=(initial_angle-angle_ext_min)/180*np.pi, final_angle=(final_angle+angle_ext_min)/180*np.pi, **layer_FETCH_CLD, tolerance=0.001)

    len_ISL_ext = 1
    cell_return = [path1, path2]
    if final_angle == 0:
        rect = gdspy.Rectangle((center[0]+radius-w/2, center[1]), (center[0]+radius+w/2, center[1]+len_ISL_ext), **layer_ISL)
        cell_return.append(rect)
    if initial_angle == -90:
        rect = gdspy.Rectangle((center[0]-len_ISL_ext, center[1]-radius+w/2), (center[0], center[1]-radius-w/2), **layer_ISL)
        cell_return.append(rect)
    if final_angle == -90:
        rect = gdspy.Rectangle((center[0], center[1]-radius+w/2), (center[0]+len_ISL_ext, center[1]-radius-w/2), **layer_ISL)
        cell_return.append(rect)
    if initial_angle == 0:
        rect = gdspy.Rectangle((center[0]+radius-w/2, center[1]), (center[0]+radius+w/2, center[1]-len_ISL_ext), **layer_ISL)
        cell_return.append(rect)
    if final_angle == 90:
        rect = gdspy.Rectangle((center[0]-len_ISL_ext, center[1]+radius+w/2), (center[0], center[1]+radius-w/2), **layer_ISL)
        cell_return.append(rect)
    if initial_angle == 90:
        rect = gdspy.Rectangle((center[0], center[1]+radius+w/2), (center[0]+len_ISL_ext, center[1]+radius-w/2), **layer_ISL)
        cell_return.append(rect)
    if initial_angle == -180:
        rect = gdspy.Rectangle((center[0]-radius-w/2, center[1]+len_ISL_ext), (center[0]-radius+w/2, center[1]), **layer_ISL)
        cell_return.append(rect)
    if final_angle == 180:
        rect = gdspy.Rectangle((center[0]-radius-w/2, center[1]), (center[0]-radius+w/2, center[1]-len_ISL_ext), **layer_ISL)
        cell_return.append(rect)
    
    return cell_return

def Splitter_12():
    Splitter_1X2 = lib.new_cell('Splitter_1X2')
    
    ## MMI 1X2
    Splitter_1X2.add(gdspy.CellReference(lib.cells["Fixed_M1X2_TE_1550"]))
    # wg 
    pos_x = len_mmi_12
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, out_1_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y_heater), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, out_1_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y_heater), **layer_FETCH_CLD)
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, out_2_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, out_2_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater), **layer_FETCH_CLD)
    # add rect for avoide the min feature
    w_rect = 8
    h_rect = 2
    x_offset_rect = np.sqrt(radius**2 - (radius-2)**2)
    origin = (pos_x+x_offset_rect, 0)
    cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    Splitter_1X2.add(cell)
    # add ISL middle
    pos_x += len_port_ext
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_12+radius), radius+r_max, w_detch, -45, 0))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_12+radius), radius-r_min, w_detch, -90, 0))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_12-radius), radius+r_max, w_detch, 0, 45))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_12-radius), radius-r_min, w_detch, 0, 90))
    # add ISL2
    pos_x += 2*radius
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius+r_max, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius-r_min, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius+r_max, w_detch, -180, -90))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius-r_min, w_detch, -180, -90))
    # next
    pos_x += len_port_ext
    pos_y = pos_y_heater

    # add ISL for heater crosstalk
    spacing_ISL = len_heater + 4*(radius+len_port_ext) + len_mmi_22
    cell=lib.new_cell('ISL_HeaterCrosstalk')
    cell.add(create_ISL((0, 0), 372, 10, 2, 2, 0))
    Splitter_1X2.add(gdspy.CellArray(cell, 2, 1, (spacing_ISL, -pos_y_heater*2), (pos_x+20, -pos_y+15)))
    Splitter_1X2.add(gdspy.CellArray(cell, 2, 1, (spacing_ISL, -pos_y_heater*2), (pos_x+20, -pos_y-5)))

    ## add  1st heater
    Splitter_1X2.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], (pos_x, pos_y)))
    pos_x += len_heater
    # add wg 
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22), **layer_FETCH_CLD)
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22), **layer_FETCH_CLD)
    # add ISL
    pos_x += len_port_ext
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius+r_max, w_detch, 0, 90))
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius-r_min, w_detch, 0, 90))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius+r_max, w_detch, -90, 0))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius-r_min, w_detch, -90, 0))
    # add ISL middle
    pos_x += radius*2
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius+r_max, w_detch, 130, 180))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius-r_min, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius+r_max, w_detch, -180, -130))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius-r_min, w_detch, -180, -90))
    # next
    pos_x += len_port_ext

    # add rect for avoide the min feature
    w_rect = 5
    h_rect = 2
    origin = (pos_x-x_offset_rect, 0)
    cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    Splitter_1X2.add(cell)

    ## the 1st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(lib.cells["Fixed_M2X2_TE_1550"], (pos_x, 0)))
    pos_x += len_mmi_22
    # wg 
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, out_1_mmi_22), (pos_x+2*radius+len_port_ext*2, pos_y_heater), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, out_1_mmi_22), (pos_x+2*radius+len_port_ext*2, pos_y_heater), **layer_FETCH_CLD)
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, out_2_mmi_22), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, out_2_mmi_22), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater), **layer_FETCH_CLD)
    # add rect for avoide the min feature
    origin = (pos_x+x_offset_rect, 0)
    cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    Splitter_1X2.add(cell)
    # add ISL middle
    pos_x += len_port_ext
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius+r_max, w_detch, -50, 0))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius-r_min, w_detch, -90, 0))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius+r_max, w_detch, 0, 50))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius-r_min, w_detch, 0, 90))
    # add ISL2
    pos_x += 2*radius
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius+r_max, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius-r_min, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius+r_max, w_detch, -180, -90))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius-r_min, w_detch, -180, -90))
    # next
    pos_x += len_port_ext
    pos_y = pos_y_heater

    ## add  2st heater
    Splitter_1X2.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], (pos_x, pos_y)))
    pos_x += len_heater
    # add wg 
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22), **layer_FETCH_CLD)
    connect_zShape3(Splitter_1X2, w_wg, len_port_ext, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22), **layer_FETCH_COR)
    connect_zShape3(Splitter_1X2, w_wg_cld, len_port_ext, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22), **layer_FETCH_CLD)
    # add ISL
    pos_x += len_port_ext
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius+r_max, w_detch, 0, 90))
    Splitter_1X2.add(ISL_curve((pos_x, pos_y_heater-radius), radius-r_min, w_detch, 0, 90))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius+r_max, w_detch, -90, 0))
    Splitter_1X2.add(ISL_curve((pos_x, -pos_y_heater+radius), radius-r_min, w_detch, -90, 0))
    # add ISL middle
    pos_x += radius*2
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius+r_max, w_detch, 130, 180))
    Splitter_1X2.add(ISL_curve((pos_x, out_2_mmi_22-radius), radius-r_min, w_detch, 90, 180))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius+r_max, w_detch, -180, -130))
    Splitter_1X2.add(ISL_curve((pos_x, out_1_mmi_22+radius), radius-r_min, w_detch, -180, -90))
    # next
    pos_x += len_port_ext
    
    # add rect for avoide the min feature
    origin = (pos_x-x_offset_rect, 0)
    cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    Splitter_1X2.add(cell)

    # the 2st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(lib.cells["Fixed_M2X2_TE_1550"], (pos_x, 0)))

    # add rect for avoide the min feature
    pos_x += len_mmi_22
    origin = (pos_x+x_offset_rect, 0)
    cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    Splitter_1X2.add(cell)

    

    return Splitter_1X2

def Splitter_tree(num=16):
    
    Splitter_1X2 = Splitter_12()
    ## define the splitter tree
    pos_x = 0
    pos_y = 0
    position_all = []
    len_splitter_1X2 = len_mmi_12 + 2*len_mmi_22 + 2*len_heater + 8*radius + 8*len_port_ext
    ST = lib.new_cell('Splitter_tree')
    N = int(np.floor(np.log2(num)))
    space_y = 4*pos_y_heater
    space_x = len_splitter_1X2 + 2*(radius + len_port_ext)
    
    for i in range(N):
        pos_x = i*space_x
        for j in range(2**i):
            pos_y = (-(2**i-1)/2*2**(N-1-i) + 2**(N-1-i)*j) * space_y
            ST.add(gdspy.CellReference(Splitter_1X2, (pos_x, pos_y)))
            position_all.append((pos_x, pos_y))
            if i < N:
                # # wg
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_22), (2*radius+len_port_ext*2, pos_y+2**(N-2-i)*space_y/2), 0)
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_22), (2*radius+len_port_ext*2, pos_y-2**(N-2-i)*space_y/2), 1)
                # wg 
                # connect_zShape3(ST, w_wg, len_port_ext, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y+out_1_mmi_12+pos_y+2**(N-2-i)*space_y/2), **layer_FETCH_COR)
                # connect_zShape3(ST, w_wg_cld, len_port_ext, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y+out_1_mmi_12+pos_y+2**(N-2-i)*space_y/2), **layer_FETCH_CLD)
                # connect_zShape3(ST, w_wg, len_port_ext, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, pos_y+out_1_mmi_12+pos_y+2**(N-2-i)*space_y/2), **layer_FETCH_COR)
                # connect_zShape3(ST, w_wg_cld, len_port_ext, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, pos_y+out_1_mmi_12+pos_y+2**(N-2-i)*space_y/2), **layer_FETCH_CLD)
                # add ISL middle
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext, pos_y+out_1_mmi_22+radius), radius+r_max, w_detch, -50, 0))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext, pos_y+out_1_mmi_22+radius), radius-r_min, w_detch, -90, 0))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext, pos_y+out_2_mmi_22-radius), radius+r_max, w_detch, 0, 50))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext, pos_y+out_2_mmi_22-radius), radius-r_min, w_detch, 0, 90))
                # # add ISL2
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext+radius*2, pos_y+2**(N-2-i)*space_y/2-radius), radius+r_max, w_detch, 90, 180))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext+radius*2, pos_y+2**(N-2-i)*space_y/2-radius), radius-r_min, w_detch, 90, 180))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext+radius*2, pos_y-2**(N-2-i)*space_y/2+radius), radius+r_max, w_detch, -180, -90))
                ST.add(ISL_curve((pos_x+len_splitter_1X2+len_port_ext+radius*2, pos_y-2**(N-2-i)*space_y/2+radius), radius-r_min, w_detch, -180, -90))
    return ST, position_all

def Splitter_tree2(num=16):
    Splitter_1X2 = Splitter_12()
    ## define the splitter tree
    pos_x = 0
    pos_y = 0
    pos_y_min = -(num-1)*pos_y_heater - 10
    pos_y_max = -pos_y_min + 10
    
    
    default_gap = len_mmi_12 + 6*(radius + len_port_ext) + len_mmi_22 + 15
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
            # if j < 2**(i-1):
            #     connect_LShape(ST, (pos_x+pos_x_pad1, pos_y+pos_y_heater), (pos_x+pos_x_pad1-len_Al_init-j*spacing_Al, pos_y_min))
            #     connect_LShape(ST, (pos_x+pos_x_pad2, pos_y+pos_y_heater), (pos_x+pos_x_pad2+len_Al_init+j*spacing_Al, pos_y_min))
            # else:
            #     connect_LShape(ST, (pos_x+pos_x_pad1, pos_y+pos_y_heater), (pos_x+pos_x_pad1-len_Al_max+(j-2**(i-1))*spacing_Al, pos_y_max))
            #     connect_LShape(ST, (pos_x+pos_x_pad2, pos_y+pos_y_heater), (pos_x+pos_x_pad2+len_Al_max-(j-2**(i-1))*spacing_Al, pos_y_max))
            # add wg
            if i == N-1:
                x_offset2 = len_Al_max - 4*(radius + len_port_ext) - len_mmi_22
            if i < N:
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_22), (2*radius+len_port_ext*2+x_offset2, pos_y+2**(N-2-i)*space_y/2), 0)
                connect_zShape2(ST, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_22), (2*radius+len_port_ext*2+x_offset2, pos_y-2**(N-2-i)*space_y/2), 1)
    return ST

def PhaseController(num=16):
    '''
    num  is even
    '''
    def connect_lineShape(cell, pos_start, len):
        path = gdspy.Path(w_wg, pos_start)
        path.segment(len, **layer_FETCH_COR)
        cell.add(path)
        path = gdspy.Path(w_wg_cld, pos_start)
        path.segment(len, **layer_FETCH_CLD)
        cell.add(path)

    def place_PhaseShift(cell, pos_PS, pos_start, len):
        len1 = pos_PS[0]
        len2 = len - len1 - len_heater
        connect_lineShape(cell, pos_start, len1)
        connect_lineShape(cell, (pos_PS[0]+len_heater, pos_start[1]), len2)
        cell.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], pos_PS))
    
    PC = lib.new_cell('PhaseController')
    num_half =int(num/2)
    pos_x = 30
    pos_y = 0
    space_x = 100
    space_y = 2*pos_y_heater

    len = space_x*(num_half-1) + len_heater + 2*pos_x
    
    for i in range(num_half):
        pos_y = (0.5 + i)*space_y
        place_PhaseShift(PC, (pos_x, pos_y), (0, pos_y), len)
        pos_x += space_x
    
    pos_x = 30
    pos_y = 0
    for i in range(num_half):
        pos_y = (-0.5 - i)*space_y
        place_PhaseShift(PC, (pos_x, pos_y), (0, pos_y), len)
        pos_x += space_x
    return PC

def PhaseController2(num=16):
    '''
    num  is even
    '''
    def place_PhaseShift(cell, pos_PS, pos_start, len):
        len1 = pos_PS[0]
        len2 = len - len1 - len_heater
        connect_lineShape(cell, pos_start, len1)
        connect_lineShape(cell, (pos_PS[0]+len_heater, pos_start[1]), len2)
        cell.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], pos_PS))
    
    PC = lib.new_cell('PhaseController')
    len_x_Al_max = 12 + spacing_Al*(num/4-1)
    pos_x_start = len_x_Al_max
    pos_y = 0
    space_y = 2*pos_y_heater
    gap = 30
    len = 2*len_heater + 2*pos_x_start + gap
    len_x_Al = 12
    len_x_Al_2 = len_x_Al
    len_x_Al_max_2 = len_x_Al_max
    pos_y_max = space_y*(num-1) + 10
    pos_y_min = -10
    # building the block
    for i in range(num):
        pos_y = (0.0 + i)*space_y
        # add Al
        if (i%2) == 1:
            # right part
            pos_x = pos_x_start + gap + len_heater
            if i < num/2:
                connect_LShape(PC, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al, pos_y_min))
                len_x_Al += spacing_Al
            else:
                connect_LShape(PC, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al_max_2, pos_y_max))
                len_x_Al_max_2 += -spacing_Al
        else:
            # left part
            pos_x = pos_x_start
            if i < num/2:
                connect_LShape(PC, (pos_x+15, pos_y), (pos_x+15-len_x_Al_2, pos_y_min))
                len_x_Al_2 += spacing_Al
            else:
                connect_LShape(PC, (pos_x+15, pos_y), (pos_x+15-len_x_Al_max, pos_y_max))
                len_x_Al_max += -spacing_Al
        # place the phase shift
        place_PhaseShift(PC, (pos_x, pos_y), (0, pos_y), len)
    return PC

def PhaseController3(num=16):
    '''
    num  is even
    '''
    def place_PhaseShift(cell, pos_PS, pos_start, len):
        len1 = pos_PS[0]
        len2 = len - len1 - len_heater
        connect_lineShape(cell, pos_start, len1)
        connect_lineShape(cell, (pos_PS[0]+len_heater, pos_start[1]), len2)
        cell.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], pos_PS))
    
    PC = lib.new_cell('PhaseController')
    # len_x_Al_max = 12 + spacing_Al*(num/2-1)
    len_x_Al_max = 12 
    pos_x_start = len_x_Al_max
    pos_y = 0
    space_y = 2*pos_y_heater
    gap = 30
    len = 2*len_heater + 2*pos_x_start + gap
    len_x_Al = 12
    len_x_Al_2 = len_x_Al
    len_x_Al_max_2 = len_x_Al_max
    pos_y_max = space_y*(num-1) + 10
    pos_y_min = -10
    j = 0
    # building the block
    for i in range(num):
        pos_y = (0.0 + i)*space_y
        # add Al
        if (i%2) == 1:
            # right part
            pos_x = pos_x_start + gap + len_heater
            connect_LShape(PC, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al, -20*33-j*10), (-3750+j*30, -H/2+dist_PAD_chip))
            len_x_Al += spacing_Al
        else:
            # left part
            pos_x = pos_x_start
            connect_LShape(PC, (pos_x+15, pos_y), (pos_x+15-len_x_Al_2, -20*32+j*10), (-3800- j*30, -H/2+dist_PAD_chip))
            len_x_Al_2 += spacing_Al
        j += 1
        # place the phase shift
        place_PhaseShift(PC, (pos_x, pos_y), (0, pos_y), len)
    return PC

def PhaseController4(num=16):
    '''
    num  is even; spacing in y direction is the same
    '''
    def place_PhaseShift(cell, pos_PS, pos_start, len):
        len1 = pos_PS[0]
        len2 = len - len1 - len_heater
        connect_lineShape(cell, pos_start, len1)
        connect_lineShape(cell, (pos_PS[0]+len_heater, pos_start[1]), len2)
        cell.add(gdspy.CellReference(lib.cells["Fixed_MH_TE_1550"], pos_PS))
    
    PC = lib.new_cell('PhaseController')
    len_x_Al_max = 12
    pos_x_start = 105
    pos_y = 0
    space_y = 2*pos_y_heater
    gap = 100
    len = 2*len_heater + 2*pos_x_start + gap+200
    position_heaters = []
    # building the block
    for i in range(num):
        pos_y = (0.0 + i)*space_y
        # add Al
        if (i%2) == 1:
            # right part
            pos_x = pos_x_start + gap + len_heater
        else:
            # left part
            pos_x = pos_x_start
        # place the phase shift
        place_PhaseShift(PC, (pos_x, pos_y), (0, pos_y), len)
        position_heaters.append((pos_x, pos_y))
    position_heaters = np.array(position_heaters)
    return PC, position_heaters

def Antennas(num=16):
    Ant = lib.new_cell('Antennas')
    def element(cell, pos_start, len):
        path = gdspy.Path(w_wg, pos_start)
        path.segment(len, **layer_FETCH_COR)
        cell.add(path)
        # path = gdspy.Path(w_wg_cld, pos_start)
        # path.segment(len, **layer_FETCH_CLD)
        # cell.add(path)
    
    pos_x = 0
    pos_y = 0
    space_y = 0.775
    len = 500
    for i in range(num):
        element(Ant, (pos_x, pos_y), len)
        pos_y += space_y
    
    # cladding of antenna 
    points = [(0, -w_wg/2-2), (len, -w_wg/2-2), (len, pos_y-space_y+w_wg/2+2), (0, pos_y-space_y+w_wg/2+2)]
    poly = gdspy.Polygon(points, **layer_FETCH_CLD)
    Ant.add(poly)
    return Ant

def Taper2Pitch(num=16):
    Link_taper = lib.new_cell('Link_taper')

    c_r90 = lib.new_cell('c_r90')
    path = gdspy.Path(w_wg, (0,0))
    path.turn(radius, 'r', **layer_FETCH_COR)
    c_r90.add(path)
    path = gdspy.Path(w_wg_cld, (0,0))
    path.turn(radius, 'r', **layer_FETCH_CLD)
    c_r90.add(path)
    
    def build(w, layer):
        pos_x = 0
        pos_y = 0
        space_x = 2
        space_y = 2*pos_y_heater
    
        # add c_r90
        for i in range(num):
            Link_taper.add(gdspy.CellReference(c_r90, (pos_x, pos_y)))
            path = gdspy.Path(w, (0, pos_y))
            path.segment(space_x*i, **layer)
            Link_taper.add(path)
            pos_x += space_x
            pos_y += space_y

        # add varius circle bend
        pos_x = pos_x + radius*2 - space_x
        space_y = 0.775
        pos_y = -num*space_x - 2*radius
        for i in range(num):
            pos_y -= space_y
            temp_radius = radius+i*space_x
            path = gdspy.Path(w, (pos_x, pos_y))
            path.arc(temp_radius, 3*np.pi/2, np.pi, **layer)
            Link_taper.add(path)
            # add straight wg
            len =  (num-1-i)*2*pos_y_heater-radius - (pos_y + temp_radius)
            path = gdspy.Path(w, ((num-1-i)*space_x+radius, (num-1-i)*2*pos_y_heater-radius))
            path.segment(len, '-y', **layer)
            Link_taper.add(path)
    
    build(w_wg, layer_FETCH_COR)
    build(w_wg_cld, layer_FETCH_CLD)

    return Link_taper

def Taper2Pitch2(num=16):
    Link_taper = lib.new_cell('Link_taper')

    c_r90 = lib.new_cell('c_r90')
    path = gdspy.Path(w_wg, (0,0))
    path.turn(radius, 'l', **layer_FETCH_COR)
    c_r90.add(path)
    path = gdspy.Path(w_wg_cld, (0,0))
    path.turn(radius, 'l', **layer_FETCH_CLD)
    c_r90.add(path)
   
    # c_r90.add(ISL_curve((0, radius), radius+100, 4, -50, -20))
    c_r90.add(ISL_curve((0, radius), radius-6, w_detch, -90, -15))
    
    w_rect = 2.5
    h_rect = 3
    R = radius + 2
    
    def build(w, layer):
        
        space_x = 0.75
        space_y = 2*pos_y_heater
        pos_x = num*space_x
        pos_y = 0

        pos_end = 8280
        # add c_r90
        for i in range(num):
            Link_taper.add(gdspy.CellReference(c_r90, (pos_x, pos_y)))
            path = gdspy.Path(w, (0, pos_y))
            path.segment(space_x*(num-i), **layer)
            Link_taper.add(path)
            len =  pos_end - pos_y
            path = gdspy.Path(w, (pos_x+radius, pos_y+radius))
            path.segment(len, '+y', **layer)
            Link_taper.add(path)
            
            # add rect for avoid 85 Deg
            if i != 0:
                x_offset_rect = radius+space_x-2-w_wg
                y_offset_rect = np.sqrt(R**2-x_offset_rect**2)
                origin = (pos_x+x_offset_rect, pos_y+radius-y_offset_rect)
                cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
                Link_taper.add(cell)
            
            pos_x += -space_x
            pos_y += space_y
    build(w_wg, layer_FETCH_COR)
    build(w_wg_cld, layer_FETCH_CLD)

    return Link_taper

def Pad(num_x=16, num_y =1, space=(120, 0), origin=(160, 0), rotation=None):
    # Pad = lib.new_cell('PAD')
    Pad = gdspy.CellArray(lib.cells["Fixed_BP"], num_x, num_y, space, origin=origin, rotation=rotation)
    return Pad

def Rect_c(origin, w, h, layer=0, datatype=1):
    rect = gdspy.Rectangle((origin[0]-w/2, origin[1]+h/2), (origin[0]+w/2, origin[1]-h/2), layer=layer, datatype=datatype)
    return rect

def Rect_cor(pos_left_up, w, h, layer=0, datatype=1):
    rect = gdspy.Rectangle(pos_left_up, (pos_left_up[0]+w, pos_left_up[1]-h), layer=layer, datatype=datatype)
    return rect

def create_Detch(pos_left_up, w, h, w_en, h_en, angle_rotate=0):
    cell1 = Rect_cor((-w/2, h/2), w, h, **layer_DETCH)
    cell1.rotate(angle_rotate)
    cell1.translate(pos_left_up[0]+w/2, pos_left_up[1]-h/2)
    cell2 = Rect_cor((-w/2-w_en, h/2+h_en), w+2*w_en, h+2*h_en, **layer_FETCH_CLD)
    cell2.rotate(angle_rotate)
    cell2.translate(pos_left_up[0]+w/2, pos_left_up[1]-h/2)
    return [cell1, cell2]

def create_ISL(pos_left_up, w, h, w_en, h_en, angle_rotate=0):
    cell1 = Rect_cor((0, 0), w, h, **layer_ISL)
    cell1.rotate(angle_rotate)
    cell1.translate(pos_left_up[0], pos_left_up[1])
    cell2 = Rect_cor((-w_en, h_en), w+2*w_en, h+2*h_en, **layer_FETCH_CLD)
    cell2.rotate(angle_rotate)
    cell2.translate(pos_left_up[0], pos_left_up[1])
    return [cell1, cell2]

def Boundary(W, H):
    w_detch = 150
    points = [(0, H/2), (W, H/2), (W, -H/2), (0, -H/2)]
    rect = gdspy.Polygon(points, **layer_DA)
    points = [(0, H/2), (-w_detch, H/2), (-w_detch, -H/2), (0, -H/2)]
    rect_detch1 = gdspy.Polygon(points, **layer_DETCH)
    points = [(W, H/2), (W+w_detch, H/2), (W+w_detch, -H/2), (W, -H/2)]
    rect_detch2 = gdspy.Polygon(points, **layer_DETCH)
    w_ext = 32
    w_fetch = w_detch + w_ext
    rect_fetch1 = Rect_c((-w_detch/2, 0), w_fetch, H+w_ext, **layer_FETCH_CLD)
    rect_fetch2 = Rect_c((W+w_detch/2, 0), w_fetch, H+w_ext, **layer_FETCH_CLD)
    rect_all = [rect, rect_detch1, rect_detch2, rect_fetch1, rect_fetch2]
    return rect_all

def Connect_splitters(cell, pos_x_start, position_end, pos_x_end=8000):
    pos = sorted(position_end, key=lambda x:x[1], reverse=True)
    
    for i in range(len(pos)):
        pos_x = pos_x_start
        pos_y = pos[i][1] + pos_y_heater + spacing_pad_x/4
        # signal 1 to left
        connect_LShape_N90(cell, (pos_x, pos_y), (pos[i][0]+pos_x_pad1, pos[i][1]+pos_y_heater))
        # GND to right
        connect_LShape_N90(cell, (pos_x_end, pos_y), (pos[i][0]+pos_x_pad1+l_heater, pos[i][1]+pos_y_heater))
        # GND to up
        connect_LShape_N90(cell, (pos[i][0] + pos_x_pad2-l_heater+50, pos_y), (pos[i][0] + pos_x_pad2-l_heater, pos[i][1]+pos_y_heater))
        pos_y += -spacing_pad_x/2
        pos_x = pos_x_start + spacing_pad_y
        # signal 2 to left
        connect_LShape_N90(cell, (pos_x, pos_y), (pos[i][0] + pos_x_pad2, pos[i][1]+pos_y_heater+5.3))

def Connect_phaseControl(cell, pos_x_start, position_end):
    num = len(position_end)
    len_x_Al_max = 12 + spacing_Al*(len(position_end)/4-1)
    len_x_Al = 12
    len_x_Al_2 = len_x_Al
    len_x_Al_max_2 = len_x_Al_max
    spacing_Al_y = 40
    pos_y_min_Al = dist_PAD_chip + spacing_pad_y + l_pad + 10
    offset_x = spacing_pad_x*4
    # left part
    for i in range(int(num/2)):
        pos_x = position_end[2*i][0]
        pos_y = position_end[2*i][1]
        if (i%2) == 1:
            offset_y = 0
        else:
            offset_y = -spacing_pad_y
        if i < num/4:
            # down direction # +y -x
            connect_LShape(cell, (pos_x+15.8, pos_y), (pos_x+15-len_x_Al_2, -H/2+pos_y_min_Al+w_GND+(num/4+i)*spacing_Al_y), (pos_x_start - i*spacing_pad_x/2, -H/2+dist_PAD_chip-offset_y))
            len_x_Al_2 += spacing_Al
        else:
            # up direction #  +x +y
            connect_LShape(cell, (pos_x+15.8, pos_y), (pos_x+15-len_x_Al_max, H/2-w_GND-pos_y_min_Al+(i-num/4*3)*spacing_Al_y), (pos_x_start + (i-num/2)*spacing_pad_x/2, H/2-dist_PAD_chip+offset_y))
            len_x_Al_max += -spacing_Al
    # right part
    for i in range(int(num/2)):
        pos_x = position_end[2*i+1][0]
        pos_y = position_end[2*i+1][1]
        if (i%2) == 1:
            offset_y = 0
        else:
            offset_y = -spacing_pad_y
        # left part
        if i < num/4:
            # down direction # -y +x
            connect_LShape(cell, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al, -H/2+pos_y_min_Al+(num/4-i)*spacing_Al_y), (pos_x_start + offset_x + i*spacing_pad_x/2, -H/2+dist_PAD_chip-offset_y))
            len_x_Al += spacing_Al
        else:
            # up direction # -y -x
            connect_LShape(cell, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al_max_2, H/2-pos_y_min_Al- (i-num/4)*spacing_Al_y), (pos_x_start + offset_x + (num/2-i)*spacing_pad_x/2, H/2-dist_PAD_chip+offset_y))
            len_x_Al_max_2 += -spacing_Al

def Connect_phaseControl2(cell, pos_x_start, position_end):
    num = len(position_end)
    len_x_Al_max = 12 + spacing_Al*(len(position_end)/4-1)
    len_x_Al = 12
    len_x_Al_2 = len_x_Al
    len_x_Al_max_2 = len_x_Al_max
    spacing_Al_y = 40
    pos_y_min_Al = dist_PAD_chip + spacing_pad_y + l_pad + 10
    offset_x = spacing_pad_x*4
    # left part
    for i in range(int(num/2)):
        pos_x = position_end[2*i][0]
        pos_y = position_end[2*i][1]
        if (i%2) == 1:
            offset_y = 0
        else:
            offset_y = -spacing_pad_y
        if i < num/4:
            # down direction # +y -x
            connect_LShape(cell, (pos_x+15.8, pos_y), (pos_x+15-len_x_Al_2, -H/2+pos_y_min_Al+w_GND+i*spacing_Al_y), (pos_x_start - i*spacing_pad_x/2, -H/2+dist_PAD_chip-offset_y))
            len_x_Al_2 += spacing_Al
        else:
            # up direction #  +x +y
            connect_LShape(cell, (pos_x+15.8, pos_y), (pos_x+15-len_x_Al_max, H/2-w_GND-pos_y_min_Al+(i-num/2)*spacing_Al_y), (pos_x_start + (i-num/2)*spacing_pad_x/2, H/2-dist_PAD_chip+offset_y))
            len_x_Al_max += -spacing_Al
    # right part
    for i in range(int(num/2)):
        pos_x = position_end[2*i+1][0]
        pos_y = position_end[2*i+1][1]
        if (i%2) == 1:
            offset_y = 0
        else:
            offset_y = -spacing_pad_y
        if i < num/4:
            # down direction # -y +x
            connect_LShape(cell, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al, -H/2+pos_y_min_Al+(num/4-i)*spacing_Al_y), (pos_x_start + offset_x + i*spacing_pad_x/2, -H/2+dist_PAD_chip-offset_y))
            len_x_Al += spacing_Al
        else:
            # up direction # -y -x
            connect_LShape(cell, (pos_x+len_heater-15, pos_y), (pos_x+len_heater-15+len_x_Al_max_2, H/2-pos_y_min_Al- (i-num/4)*spacing_Al_y), (pos_x_start + offset_x + (num/2-i)*spacing_pad_x/2, H/2-dist_PAD_chip+offset_y))
            len_x_Al_max_2 += -spacing_Al

def Connect_phaseControl4(cell, position_start, position_x_end):
    num = len(position_start)
    for i in range(num):
        pos_x = position_start[i][0]
        pos_y = position_start[i][1]
        connect_LShape_N90(cell, (position_x_end, pos_y+spacing_pad_y/4), (pos_x+5.5, pos_y))

def Connect_phaseControl3(cell, position_start, position_x_end):
    num = len(position_start)
    for i in range(num):
        pos_x = position_start[i][0]
        pos_y = position_start[i][1]
        connect_1Shape(cell, (pos_x, pos_y), position_x_end)
        
def Connect_phaseControl_GND(cell, position_start, position_x_end):
    num = len(position_start)
    for i in range(num):
        pos_x = position_start[i][0]
        pos_y = position_start[i][1]
        if pos_x > 8200:
            connect_1Shape(cell, (pos_x, pos_y), position_x_end)

def taper(pos, len, w1, w2):
    rect = gdspy.Rectangle((pos[0], pos[1]+w_wg_cld/2), (pos[0]+len, pos[1]-w_wg_cld/2), **layer_FETCH_CLD)
    taper1 = gdspy.Polygon([(pos[0], pos[1]+w1/2), (pos[0], pos[1]-w1/2), (pos[0]+len, pos[1]-w2/2), (pos[0]+len, pos[1]+w2/2)], **layer_FETCH_COR)
    return [rect, taper1]

def TestingComponent():
    Testing = lib.new_cell('TestingComponents')
    cell_grating = lib.cells['Fixed_GC_TE_1550']
    cell_grating_TM = lib.cells['Fixed_GC_TM_1550']
    cell_mmi12 = lib.cells['Fixed_M1X2_TE_1550']
    cell_mmi22 = lib.cells['Fixed_M2X2_TE_1550']
    cell_heater = lib.cells['Fixed_MH_TE_1550']
    cell_pbs = lib.cells['Fixed_PBS_1550']
    pos_x = 0
    pos_y = 0
    # add grating pair
    len_gratingPair = 2000
    cell = lib.new_cell('GC_pair')
    cell.add(gdspy.CellReference(cell_grating))
    connect_zShape4(cell, w_wg, 0, (0,0), (len_gratingPair, 0))
    cell.add(gdspy.CellReference(cell_grating, (len_gratingPair, 0), rotation=180))
    Testing.add(gdspy.CellReference(cell, (0, pos_y)))

    # add PBS
    pos_x = 500
    pos_y -= 60
    pos_mmi = (500, 0)
    cell = lib.new_cell('pbs')
    # TE
    cell.add(gdspy.CellReference(cell_grating))
    connect_zShape4(cell, w_wg, 0, (0,0), (pos_x, 0))
    cell.add(gdspy.CellReference(cell_pbs, (pos_x, 0)))
    connect_zShape4(cell, 0.5, 0, (pos_x+len_PBS,0), (1970, 0))
    cell.add(taper((1970, 0), 30, 0.5, w_wg))
    connect_zShape4(cell, w_wg, 10, (pos_x+len_PBS,-20), (2000, -127))
    cell.add(gdspy.CellArray(cell_grating, 1, 2, (0, 127), (2000, 0), rotation=180))
    # TM
    cell.add(gdspy.CellReference(cell_grating_TM, (0, -127*2)))
    cell.add(taper((0, -127*2), 30, 0.5, w_wg))
    connect_zShape4(cell, w_wg, 0, (30, -127*2), (pos_x, -127*2))
    cell.add(gdspy.CellReference(cell_pbs, (pos_x, -127*2)))
    connect_zShape4(cell, 0.5, 0, (pos_x+len_PBS,-127*2), (2000, -127*2))
    connect_zShape4(cell, w_wg, 10, (pos_x+len_PBS,-127*2-20), (1970, -127*3))
    cell.add(taper((1970, -127*3), 30, w_wg, 0.5))
    cell.add(gdspy.CellArray(cell_grating_TM, 1, 2, (0, 127), (2000, -127*2), rotation=180))
    Testing.add(gdspy.CellReference(cell, (0, pos_y)))

    # add MZI based on 1X2 MMI
    pos_x = 0
    pos_y = pos_y - 4*127
    pos_mmi = (815, 0)
    cell = lib.new_cell('MZI_12_mmi')
    cell.add(gdspy.CellReference(cell_grating))
    connect_zShape4(cell, w_wg, 0, (0,0), pos_mmi)
    cell.add(gdspy.CellReference(cell_mmi12, pos_mmi))
    pos_x += pos_mmi[0]
    pos_x += len_mmi_12
    # add rect
    w_rect = 8
    h_rect = 2
    x_offset_rect = np.sqrt(radius**2 - (radius-2)**2)
    origin = (pos_x+x_offset_rect, 0)
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    # add AL
    connect_LShape_N90(Testing, (pos_x+2*radius+2*len_port_ext+ 15, pos_y+pos_y_heater), (200, -1200))
    connect_LShape_N90(Testing, (pos_x+2*radius+2*len_port_ext+len_heater-10, pos_y+pos_y_heater), (1585.8, -950))
    # add wg
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, out_1_mmi_12), (pos_x+2*radius+2*len_port_ext, pos_y_heater))
    cell.add(gdspy.CellReference(cell_heater, (pos_x+2*radius+2*len_port_ext, pos_y_heater)))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, out_2_mmi_12), (pos_x+len_heater+2*radius+2*len_port_ext, -pos_y_heater))
    pos_x += 2*radius+2*len_port_ext
    pos_x += len_heater
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_y_heater), (pos_x+2*radius+2*len_port_ext, out_1_mmi_12))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, -pos_y_heater), (pos_x+2*radius+2*len_port_ext, out_2_mmi_12))
    pos_x += 2*radius+2*len_port_ext
    # add rect
    origin = (pos_x-x_offset_rect, 0)
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    # add mmi
    cell.add(gdspy.CellReference(cell_mmi12, (pos_x+len_mmi_12, 0), rotation=180))
    pos_x += len_mmi_12
    connect_zShape4(cell, w_wg, 0, (pos_x, 0), (2000, 0))
    cell.add(gdspy.CellReference(cell_grating, (2000, 0), rotation=180))
    Testing.add(gdspy.CellReference(cell, (0, pos_y)))

    

    # add MZI based on 2X2 MMI
    pos_x = 0
    pos_y -= 127
    w_rect = 5
    pos_mmi = (700, -127/2)
    cell = lib.new_cell('MZI_22_mmi')
    cell.add(gdspy.CellArray(cell_grating, 1, 2, (0, -127)))
    # add two straight wg
    pos_x = pos_mmi[0]-2*radius-2*len_port_ext
    connect_zShape4(cell, w_wg, 0, (0,0), (pos_x, 0))
    connect_zShape4(cell, w_wg, 0, (0,-127), (pos_x, -127))
    #
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, 0), (pos_mmi[0], pos_mmi[1]+out_1_mmi_22))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x,-127), (pos_mmi[0], pos_mmi[1]+out_2_mmi_22))
    #
    origin = (pos_mmi[0]-x_offset_rect, pos_mmi[1])
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    cell.add(gdspy.CellReference(cell_mmi22, pos_mmi))
    pos_x = pos_mmi[0] + len_mmi_22
    # add AL
    connect_LShape_N90(Testing, (pos_x+2*radius+2*len_port_ext+ 15, pos_y+pos_y_heater-127/2), (200+120, -1200))
    connect_LShape_N90(Testing, (pos_x+2*radius+2*len_port_ext+len_heater-10, pos_y+pos_y_heater-127/2), (1585.8, -950))
    #
    origin = (pos_x+x_offset_rect, pos_mmi[1])
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    # add wg
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]+out_1_mmi_22), (pos_x+2*radius+2*len_port_ext, pos_mmi[1]+pos_y_heater))
    # add heater
    cell.add(gdspy.CellReference(cell_heater, (pos_x+2*radius+2*len_port_ext, pos_mmi[1]+pos_y_heater)))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]+out_2_mmi_22), (pos_x+len_heater+2*radius+2*len_port_ext, pos_mmi[1]-pos_y_heater))
    pos_x += 2*radius+2*len_port_ext
    pos_x += len_heater
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]+pos_y_heater), (pos_x+2*radius+2*len_port_ext, pos_mmi[1]+out_1_mmi_22))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]-pos_y_heater), (pos_x+2*radius+2*len_port_ext, pos_mmi[1]+out_2_mmi_22))
    pos_x += 2*radius+2*len_port_ext
    #
    origin = (pos_x-x_offset_rect, pos_mmi[1])
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    cell.add(gdspy.CellReference(cell_mmi22, (pos_x, pos_mmi[1])))
    pos_x += len_mmi_22
    #
    origin = (pos_x+x_offset_rect, pos_mmi[1])
    temp_cell = Rect_c(origin, w_rect, h_rect, **layer_FETCH_CLD)
    cell.add(temp_cell)
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]+out_1_mmi_22), (pos_x+2*radius+2*len_port_ext,0))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, pos_mmi[1]+out_2_mmi_22), (pos_x+2*radius+2*len_port_ext,-127))
    pos_x += 2*radius+2*len_port_ext
    connect_zShape4(cell, w_wg, 0, (pos_x,0), (2000, 0))
    connect_zShape4(cell, w_wg, 0, (pos_x,-127), (2000, -127))
    cell.add(gdspy.CellArray(cell_grating, 1, 2, (0, 127), (2000, 0), rotation=180))
    Testing.add(gdspy.CellReference(cell, (0, pos_y)))
    
    # add 1X2 Splitter
    pos_x = 500
    pos_y = pos_y - 2.5*127
    cell = lib.new_cell('Sp')
    cell_splitter = lib.cells['Splitter_1X2']
    cell.add(gdspy.CellReference(cell_grating))
    connect_zShape4(cell, w_wg, 0, (0,0), (pos_x,0))
    cell.add(gdspy.CellReference(cell_splitter, (pos_x, 0)))
    # add AL
    connect_LShape_N90(Testing, (pos_x+pos_x_pad1+4.8, pos_y+pos_y_heater), (200+120*3+8, -1200))
    connect_NShape(Testing, (pos_x+pos_x_pad2+20-len_heater, pos_y+pos_y_heater), len_y1 = 50, len_x=-(pos_x+pos_x_pad2+20-len_heater-(200+120*2)), len_y2=(pos_y+pos_y_heater+1200+50), pos_stop_x=(200+120*2))
    connect_LShape(Testing, (pos_x+pos_x_pad1-20+len_heater, pos_y+pos_y_heater), (pos_x+pos_x_pad1-20+len_heater, -1200), (200+120*4, -1200))
    connect_LShape(Testing, (pos_x+pos_x_pad2, pos_y+pos_y_heater), (pos_x+pos_x_pad2, -1200), (200+120*4, -1200))
    #
    pos_x +=len_splitter_1X2
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, out_1_mmi_22), (pos_x+2*radius+2*len_port_ext,127/2))
    connect_zShape4(cell, w_wg, len_port_ext, (pos_x, out_2_mmi_22), (pos_x+2*radius+2*len_port_ext,-127/2))
    pos_x += 2*radius+2*len_port_ext
    connect_zShape4(cell, w_wg, 0, (pos_x, 127/2), (2000, 127/2))
    connect_zShape4(cell, w_wg, 0, (pos_x,-127/2), (2000, -127/2))
    cell.add(gdspy.CellArray(cell_grating, 1, 2, (0, 127), (2000, 127/2), rotation=180))
    Testing.add(gdspy.CellReference(cell, (0, pos_y)))

    # add pad
    Testing.add(Pad(1, 5, space=(0, spacing_pad_x), origin=(200, pos_y-200), rotation=-90))


    return Testing


if __name__ == '__main__':
    
    # define the parameters
    num = 64
    W = 10000
    H = 10000

    # add box boundary
    box = Boundary(W, H)
    DEVICE.add(box)

    dist_FA_chip = 500
    dist_FA_pad = 800 + 60
    dist_FA = 127
    dist_PAD_chip = 100
    num_pad_x = 25

    # add pad
    y_pad1 = H/2 - dist_PAD_chip - 120*5-10
    y_pad2 = y_pad1 - w_pad
    y_pad3 = y_pad1 - 5
    # the y direction pad left
    DEVICE.add(Pad(1, 63, space=(0, -spacing_pad_x), origin=(dist_PAD_chip+w_pad/2, y_pad1)))
    DEVICE.add(Pad(1, 63, space=(0, -spacing_pad_x), origin=(dist_PAD_chip + spacing_pad_x+w_pad/2, y_pad2)))
    # the y direction pad, right
    DEVICE.add(Pad(1, 64, space=(0, -spacing_pad_x), origin=(W-dist_PAD_chip-w_pad/2, y_pad3)))

    # add edge coupler
    pos_x = len_EC
    pos_y = -H/2+dist_FA_chip+dist_FA*2+25
    DEVICE.add(gdspy.CellArray(lib.cells['Fixed_EC_1550'], 1, 3, (0, -dist_FA), origin=(pos_x, pos_y)))

    # add wg for alignment
    len_alignment = 500
    pts = [(pos_x, pos_y-dist_FA), (pos_x+len_alignment, pos_y-dist_FA), (pos_x+len_alignment, pos_y-2*dist_FA), (pos_x, pos_y-2*dist_FA)]
    path = gdspy.FlexPath(pts, 0.45, corners='circular bend', bend_radius=20, **layer_FETCH_COR)
    DEVICE.add(path)
    path = gdspy.FlexPath(pts, w_wg_cld, corners='circular bend', bend_radius=20, **layer_FETCH_CLD)
    DEVICE.add(path)

    # add PBS 
    pos_PBS = 368
    len_PBS = 87.2
    pos_PBS_TE = 20
    connect_lineShape(DEVICE, (pos_x, pos_y), pos_PBS, '+x')
    pos_x += pos_PBS
    DEVICE.add(gdspy.CellReference(lib.cells['Fixed_PBS_1550'], (pos_x, pos_y)))

    # add GC_TM_1550
    pos_GC_TM = (600, -2040)
    DEVICE.add(gdspy.CellReference(lib.cells['Fixed_GC_TM_1550'], pos_GC_TM))

    # connect to GC_TM_1550
    pos_x += len_PBS
    offset_x_TM = 30
    offset_x_TE = 60
    pts = [(pos_x, pos_y), (pos_x+offset_x_TM, pos_y), (pos_x+offset_x_TM, pos_GC_TM[1]), pos_GC_TM]
    path = gdspy.FlexPath(pts, 0.5, corners='circular bend', bend_radius=20, **layer_FETCH_COR)
    DEVICE.add(path)
    path = gdspy.FlexPath(pts, w_wg_cld, corners='circular bend', bend_radius=20, **layer_FETCH_CLD)
    DEVICE.add(path)
    # ISL 1
    DEVICE.add(ISL_curve((pos_x+offset_x_TM-radius, pos_y+radius), radius+r_max, w_detch, -90, 0))
    DEVICE.add(ISL_curve((pos_x+offset_x_TM-radius, pos_y+radius), radius-r_min, w_detch, -90, 0))
    #2
    DEVICE.add(ISL_curve((pos_x+offset_x_TM-radius, pos_GC_TM[1]-radius), radius+r_max, w_detch, 0, 90))
    DEVICE.add(ISL_curve((pos_x+offset_x_TM-radius, pos_GC_TM[1]-radius), radius-r_min, w_detch, 0, 90))
    
    # connet to splitter trees
    pos_y += -20
    pos_input = (350, 120*4)
    len_input_y1 = (pos_input[1] - pos_y - radius*4)/2
    pts = [(pos_x, pos_y), (pos_x+offset_x_TE, pos_y), (pos_x+offset_x_TE, pos_y+len_input_y1), (pos_input[0]-30, pos_y+len_input_y1), (pos_input[0]-30, pos_input[1]), pos_input]
    path = gdspy.FlexPath(pts, w_wg, corners='circular bend', bend_radius=20, **layer_FETCH_COR)
    DEVICE.add(path)
    path = gdspy.FlexPath(pts, w_wg_cld, corners='circular bend', bend_radius=20, **layer_FETCH_CLD)
    DEVICE.add(path)
    #1
    DEVICE.add(ISL_curve((pos_x+offset_x_TE-radius, pos_y+radius), radius+r_max, w_detch, -90, 0))
    DEVICE.add(ISL_curve((pos_x+offset_x_TE-radius, pos_y+radius), radius-r_min, w_detch, -90, 0))
    #2
    DEVICE.add(ISL_curve((pos_x+offset_x_TE-radius, pos_y+len_input_y1-radius), radius+r_max, w_detch, 0, 90))
    DEVICE.add(ISL_curve((pos_x+offset_x_TE-radius, pos_y+len_input_y1-radius), radius-r_min, w_detch, 0, 90))
    #3
    DEVICE.add(ISL_curve((pos_input[0]-30+radius, pos_y+len_input_y1+radius), radius+r_max, w_detch, -180, -90))
    DEVICE.add(ISL_curve((pos_input[0]-30+radius, pos_y+len_input_y1+radius), radius-r_min, w_detch, -180, -90))
    #4
    DEVICE.add(ISL_curve((pos_input[0]-30+radius, pos_input[1]-radius), radius+r_max, w_detch, 90, 180))
    DEVICE.add(ISL_curve((pos_input[0]-30+radius, pos_input[1]-radius), radius-r_min, w_detch, 90, 180))

    # add splitter tree
    pos_x = pos_input[0]
    pos_y = pos_input[1]
    [st, position_splitters] = Splitter_tree(num)
    DEVICE.add(gdspy.CellReference(st, (pos_x, pos_y)))
    # add Al for splitter tree
    position_splitters = np.array(position_splitters)
    temp_pos_splitters = position_splitters+[pos_x, pos_y]
    Connect_splitters(DEVICE, dist_PAD_chip+w_pad/2, position_splitters+[pos_x, pos_y], 8300)

    # add phase controller
    box_st = st.get_bounding_box()
    pos_x += box_st[1][0]
    [pc, position_pc] = PhaseController4(num)
    DEVICE.add(gdspy.CellReference(pc, (pos_x, -(num-1)*pos_y_heater+pos_y)))
    # add Al for phase Controler
    Connect_phaseControl4(DEVICE, position_pc+[pos_x+len_heater-15, -(num-1)*pos_y_heater+pos_y], W-dist_PAD_chip)
    # # add GND for phase Control
    Connect_phaseControl_GND(DEVICE, position_pc+[pos_x+15.7, -(num-1)*pos_y_heater+pos_y], 8300)

    # add GND
    # GND around phase control 
    pos_x_GND = position_pc[0][0]+pos_x+15.7-135
    # right
    DEVICE.add(Rect_cor((pos_x_GND+15, 4400), 120, 7800, **layer_M1))
    # left
    # DEVICE.add(Rect_cor((pos_x_GND-120-35, 4400), 120, 7800, **layer_M1))
    # other pad x direction
    DEVICE.add(Rect_cor((dist_PAD_chip-10, 4500), 9820, 120, **layer_M1))
    DEVICE.add(Rect_cor((dist_PAD_chip-7.5, 4500-2.5), 195, 115, **layer_PASS))
    DEVICE.add(Rect_cor((dist_PAD_chip+9810-195-2.5, 4500-2.5), 195, 115, **layer_PASS))
    # right bottom
    DEVICE.add(Rect_cor((8227.5, -3360), 1682.5, 120, **layer_M1))
    DEVICE.add(Rect_cor((7500+2410-2.5-195, -3360-2.5), 195, 115, **layer_PASS))

    # add wg link to half-wl pitch
    box_pc = pc.get_bounding_box()
    pos_x += box_pc[1][0]
    link = Taper2Pitch2(num)
    DEVICE.add(gdspy.CellReference(link, (pos_x, -(num-1)*pos_y_heater+pos_y )))
    
    ## add ISL at EC input
    w_ISL = 500
    h_ISL = 10
    pos_ISL = (40, -4180)
    cell = lib.new_cell('ISL1')
    cell.add(create_ISL((0,0), w_ISL, h_ISL, 2, 2, 45/180*np.pi))
    DEVICE.add(gdspy.CellArray(cell, 5, 1, (150, 0), pos_ISL))
    DEVICE.add(gdspy.CellArray(cell, 1, 5, (0, -150), (390, -3837.03), 90))
    DEVICE.add(gdspy.CellArray(cell, 1, 5, (0, -150), (390, -4880), 90))
    w_ISL = 80
    h_ISL = 10
    pos_ISL = (40, -4250)
    cell = lib.new_cell('ISL2')
    cell.add(create_ISL((0,0), w_ISL, h_ISL, 2, 2, -45/180*np.pi))
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (150, -127), pos_ISL))
    
    ## add ISL at output 
    # the left two
    w_ISL = 350
    h_ISL = 10
    pos_ISL = (9040, 4530)
    cell = lib.new_cell('ISL3')
    cell.add(create_ISL((0,0), w_ISL, h_ISL, 2, 2, 45/180*np.pi))
    DEVICE.add(gdspy.CellArray(cell, 2, 5, (-250, 50), pos_ISL))
    # for cut
    DEVICE.add(gdspy.CellArray(cell, 2, 5, (-250, 50), (pos_ISL[0], -pos_ISL[1]-440)))
    # the right
    w_ISL = 350
    h_ISL = 10
    pos_ISL = (9290, 4530)
    cell = lib.new_cell('ISL4')
    cell.add(create_ISL((0,0), w_ISL, h_ISL, 2, 2, 45/180*np.pi))
    cell.add(create_ISL((610,-h_ISL*np.cos(np.pi/4)), w_ISL, h_ISL, 2, 2, 135/180*np.pi))
    DEVICE.add(gdspy.CellArray(cell, 1, 5, (-250, 50), pos_ISL))

    w_ISL = 10
    h_ISL = 10
    cell = lib.new_cell('ISL_unit')
    cell.add(create_ISL((0,0), w_ISL, h_ISL, 2, 2, 0))
    ## add ISL unit in down chip
    pos_ISL = (1100, -3340)
    DEVICE.add(gdspy.CellArray(cell, 340, 7, (20, -20), pos_ISL))
    pos_ISL = (1100, -3500)
    DEVICE.add(gdspy.CellArray(cell, 435, 10, (20, -20), pos_ISL))
    pos_ISL = (1100, -3720)
    DEVICE.add(gdspy.CellArray(cell, 19, 58, (20, -20), pos_ISL))
    ## add ISL unit in up chip
    pos_ISL = (300, 4530)
    DEVICE.add(gdspy.CellArray(cell, 420, 5, (20, 20), pos_ISL))

    ## add ISL unit in EC
    pos_ISL = (80, -3330)
    DEVICE.add(gdspy.CellArray(cell, 45, 7, (20, -20), pos_ISL))

    ## add ISL unit in splitter tree
    # 1st heater
    for i in range(6):
        for j in range(128):
            pos_ISL = (spacing_splitter*i+419, 60*j-3305)
            flag_build = 1
            # grating 
            if (np.abs(pos_ISL[0]-pos_GC_TM[0]+160) < 200) & (np.abs(pos_ISL[1]-pos_GC_TM[1]) < 40):
                flag_build = 0
            # heater
            for k in range(len(temp_pos_splitters)):
                if (np.abs(pos_ISL[0]-temp_pos_splitters[k][0]-94) < 40) & (np.abs(pos_ISL[1]-temp_pos_splitters[k][1]-40) < 40):
                    flag_build = 0
            if flag_build == 1:
                DEVICE.add(gdspy.CellArray(cell, 20, 2, (20, 20), pos_ISL))
    # 2nd heater
    for i in range(6):
        for j in range(128):
            pos_ISL = (spacing_splitter*i+1046, 60*j-3305)
            flag_build = 1
            # heater
            for k in range(len(temp_pos_splitters)):
                if (np.abs(pos_ISL[0]-temp_pos_splitters[k][0]-724) < 40) & (np.abs(pos_ISL[1]-temp_pos_splitters[k][1]-40) < 40):
                    flag_build = 0
            # grating
            if (np.abs(pos_ISL[0]-1047) < 40) & (np.abs(pos_ISL[1]+1942) < 40):
                    flag_build = 0
            if flag_build == 1:
                DEVICE.add(gdspy.CellArray(cell, 20, 2, (20, 20), pos_ISL))
    # 1st 2X2
    for i in range(6):
        for j in range(128):
            flag_build = 1
            pos_ISL = (spacing_splitter*i+870, 60*j-3305)
            for k in range(len(temp_pos_splitters)):
                if (np.abs(pos_ISL[0]-temp_pos_splitters[k][0]-520) < 40) & (np.abs(pos_ISL[1]-temp_pos_splitters[k][1]) < 40):
                    flag_build = 0
            # grating
            if (np.abs(pos_ISL[0]-870) < 40) & (np.abs(pos_ISL[1]+2045) < 40):
                    flag_build = 0
            if flag_build == 1:
                DEVICE.add(gdspy.CellArray(cell, 6, 2, (20, 20), pos_ISL))
    # 2st 2X2
    for i in range(6):
        for j in range(128):
            flag_build = 1
            pos_ISL = (spacing_splitter*i+1500, 60*j-3305)
            for k in range(len(temp_pos_splitters)):
                if (np.abs(pos_ISL[0]-temp_pos_splitters[k][0]-1150) < 40) & (np.abs(pos_ISL[1]-temp_pos_splitters[k][1]) < 40):
                    flag_build = 0
            if flag_build == 1:
                DEVICE.add(gdspy.CellArray(cell, 6, 2, (20, 20), pos_ISL))

    ## add ISL unit in phase controller
    pos_x_start = 8370
    pos_y_start = -3245
    # add long rect ISL 
    temp_cell = lib.new_cell('ISL_Crosstalk_phase')
    temp_cell.add(create_ISL((0,0), 1200, 10, 2, 2, 0))
    DEVICE.add(gdspy.CellArray(temp_cell, 1, 64, (0, pos_y_heater*2), (pos_x_start, pos_y_start+20)))
    # middle of heater
    for i in range(1):
        for j in range(64):
            pos_ISL = (spacing_splitter*i+pos_x_start, 120*j+pos_y_start)
            DEVICE.add(gdspy.CellArray(cell, 60, 2, (20, 40), pos_ISL))
    # the left heater 1
    # for i in range(1):
    #     for j in range(32):
    #         pos_ISL = (spacing_splitter*i+pos_x_start, 240*j+pos_y_start-60)
    #         DEVICE.add(gdspy.CellArray(cell, 17, 2, (20, 20), pos_ISL))
    # the left heater 2
    for i in range(1):
        for j in range(32):
            pos_ISL = (spacing_splitter*i+pos_x_start+20*19, 240*j+pos_y_start-60)
            DEVICE.add(gdspy.CellArray(cell, 40, 2, (20, 20), pos_ISL))
    # the right heater 1
    # for i in range(1):
    #     for j in range(32):
    #         pos_ISL = (spacing_splitter*i+pos_x_start, 240*j+pos_y_start+60)
    #         DEVICE.add(gdspy.CellArray(cell, 24, 2, (20, 20), pos_ISL))
    # the right heater 2
    # for i in range(1):
    #     for j in range(32):
    #         pos_ISL = (spacing_splitter*i+pos_x_start+20*25, 240*j+pos_y_start+60)
    #         DEVICE.add(gdspy.CellArray(cell, 18, 2, (20, 20), pos_ISL))
    # the right heater 3
    for i in range(1):
        for j in range(32):
            pos_ISL = (spacing_splitter*i+pos_x_start+20*44, 240*j+pos_y_start+60)
            DEVICE.add(gdspy.CellArray(cell, 15, 2, (20, 20), pos_ISL))
    # the right
    for i in range(1):
        for j in range(63):
            pos_ISL = (spacing_splitter*i+9640, 120*j+pos_y_start)
            DEVICE.add(gdspy.CellArray(cell, 8, 5, (20, 20), pos_ISL))

    # add Testing components
    pos_testing = (2000, -3720)
    DEVICE.add(gdspy.CellArray(TestingComponent(), 2, 1, (3000, 0), pos_testing))
    ## add ISL unit 
    pos_ISL = (pos_testing[0]+902, pos_testing[1]-683.5)
    DEVICE.add(gdspy.CellArray(cell, 18, 2, (20, -20), pos_ISL))
    ## add ISL unit 
    pos_ISL = (pos_testing[0]+1220, pos_testing[1]-683.5-254)
    DEVICE.add(gdspy.CellArray(cell, 18, 2, (20, -20), pos_ISL))
    ## add rect 
    pos_ISL = (pos_testing[0]+902, pos_testing[1]-683.5+127-60+3.5)
    DEVICE.add(gdspy.CellArray(lib.cells['ISL_HeaterCrosstalk'], 1, 2, (20, -20), pos_ISL))
    ## add ISL rect
    pos_ISL = (pos_testing[0]+600+3000-23, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(lib.cells['ISL_HeaterCrosstalk'], 1, 2, (20, -20), pos_ISL))
    ## add rect 
    pos_ISL = (pos_testing[0]+1200+3000+14, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))
    pos_ISL = (pos_testing[0]+1200+3000+14+60, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))
    pos_ISL = (pos_testing[0]+1200+3000+14+120, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))
    pos_ISL = (pos_testing[0]+1200+3000+14+180, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))
    pos_ISL = (pos_testing[0]+1200+3000+14+240, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))
    pos_ISL = (pos_testing[0]+1200+3000+14+300, pos_testing[1]-960+23-0.5)
    DEVICE.add(gdspy.CellArray(cell, 5, 2, (10, -20), pos_ISL))

    lib.write_gds('test_main_'+str(num)+'_R90_V4.gds')

