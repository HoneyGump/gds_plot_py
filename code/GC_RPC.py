import numpy as np
import gdspy
import scipy.io as scio
import Photonics_PDK as GC_PC

w_wg = 0.5
w_etch = 3
w = 10

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

def gc_rect(cell, pa):
    l_grating = 500
    xp = -l_grating - 6 # xp is the position of x
    i=0
    while i<len(pa):
        a =  float(pa[i]) # here a is the trench that will be etched, b is the teeth
        b =  float(pa[i+1])

        points = [(xp, -w/2), (xp, w/2), (xp-a, w/2), (xp-a, -w/2)]
        poly = gdspy.Polygon(points, **ld_fulletch) 
        cell.add(poly)

        pitch = a + b
        xp += -pitch
        i += 2
    
    points = [(0, w_wg/2), (-l_grating, w/2), (xp-10, w/2), (xp-10, w/2+w_etch), (-l_grating, w/2+w_etch), (0, w_wg/2+w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    cell.add(poly)

    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
    cell.add(poly)
    return cell

def gc_focusing(cell, pa,  xp=22, theta=25):
    # xp is the length of taper
    GC_theta = (theta+3)/180*np.pi
    GC_theta2 = theta/180*np.pi
    i = 0
    while i<len(pa):
        a =  float(pa[i])
        b =  float(pa[i+1])
        arc = gdspy.Round(
            (0, 0),
            xp+a,
            inner_radius=xp,
            initial_angle= -GC_theta+np.pi,
            final_angle= GC_theta+np.pi,
            number_of_points=300,
            **ld_grating
        )
        cell.add(arc)

        pitch = a + b   
        xp += pitch
        i += 2

    GC_theta = GC_theta2
    points = [(0, w_wg/2), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta)), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta) + w_etch), (0, w_wg/2 + w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    cell.add(poly)

    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
    cell.add(poly)

def gc_FA(cell, gc, origin=(0,0)):
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (origin[0],-127)))
    
    l_portIn = 40
    l_portOut = l_portIn
    path_connect = gdspy.Path(w_wg)
    path_connect.segment(l_portIn)
    path_connect.turn(10, "r")
    path_connect.segment(107)
    path_connect.turn(10, "r")
    path_connect.segment(l_portOut)

    path_connect2 = gdspy.Path(w_wg+6)
    path_connect2.segment(l_portIn)
    path_connect2.turn(10, "r")
    path_connect2.segment(107)
    path_connect2.turn(10, "r")
    path_connect2.segment(l_portOut)
    
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor')
    cell.add(path_connect_positive)
    return cell

def gc_line(cell, gc, origin=(0,0), l=200):
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (l+origin[0], origin[1]), rotation=180))
    path_connect = gdspy.Path(w_wg)
    path_connect.segment(l)
    path_connect2 = gdspy.Path(w_wg+6)
    path_connect2.segment(l)
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor',layer=1, datatype=1)
    cell.add(path_connect_positive)
    return cell

def generator_parameters(pitch, ff, num_pitch):
    pa = [0]*num_pitch*2
    for i in range(num_pitch):
        pa[2*i] = round(pitch*(1-ff), 3)
        pa[2*i+1] = round(pitch*ff, 3)
    return pa

def readParameters(filename):
    data = np.loadtxt(filename)
    data = np.round(data, 4)
    data = list(data)
    data.pop(0)
    data.append(data[-1])
    return data

def gc_PC_apodized(lib, filename0, D, d_goal, period_num=29, l_taper_a=500, l_grating=30):
    a = 0.23
    w_gc = w
    num_y = np.floor(w/(a*np.sqrt(3)))
    pitch_y = a*np.sqrt(3) # pitch in the y direction
    # create the main body of phtonic crystal grating coupler
    filename = filename0 
    grating = lib.new_cell(filename)
    for ii in range(period_num):
        # this is for a variable period
        if ii == 0:
            x_start = -l_taper_a
        else:
            x_start += -d_goal[(ii,0)]
        
        # create the cell for reference
        D_temp = D[(ii,0)]
        name_cell = "D"+str(int(D_temp*1e3))
        if name_cell not in lib.cells:
            circles = lib.new_cell(name_cell)
            circle = gdspy.Round((0, 0), D_temp/2, number_of_points=128, **ld_grating)
            circles.add(circle)
        else:
            Cell_all = lib.cells
            circles = Cell_all[name_cell]
        
        # create the 3 column of hole
        for x_index in range(3):
            num_y = np.floor(w/pitch_y)
            if x_index == 1:
                num_y = num_y + 1
            for y_index in range(int(num_y)):
                grating.add(gdspy.CellReference(circles, (x_start + x_index*a/2, -(num_y -1)*pitch_y/2+pitch_y*y_index)))

    # create the etche region of phtonic crystal grating coupler
    points = [(0, w_wg/2), (-l_taper_a, w_gc/2), (-l_taper_a-l_grating, w_gc/2), (-l_taper_a-l_grating, w_gc/2+w_etch), (-l_taper_a, w_gc/2+w_etch), (0, w_wg/2+w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    grating.add(poly)
    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0, 0), (1, 0))
    grating.add(poly)
    return grating


lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")

# load data for Air
filename = './data_apodized/apod_2D_params_Air_8Deg.txt'
data = readParameters(filename)

text = 'Air 1'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, 50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

space = 0
for complement in [0, 0.005, -0.005]:
    data_mod = list(np.array(data) + complement)
    cellname = 'GC_Air_Apodized_8Deg_' + str(int(complement*1e3))
    # create the rect grating for Air
    GC_rect_Apodized_Air = lib.new_cell(cellname)
    gc_rect(GC_rect_Apodized_Air, data)
    GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_rect_Apodized_Air)
    DEVICES.add(gdspy.CellReference(GC_line, (0, space)))
    space += -100

text = 'Air 2'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space-50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

space += -100
for complement in [0, 0.005, -0.005]:
    data_mod = list(np.array(data) + complement)
    cellname = 'GC_Air_Apodized_8Deg_focusing_' + str(int(complement*1e3))
    # create the rect grating for Air
    GC_focusing_Apodzied_Air = lib.new_cell(cellname)
    gc_focusing(GC_focusing_Apodzied_Air, data)
    GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_focusing_Apodzied_Air, l = 1160)
    DEVICES.add(gdspy.CellReference(GC_line, (-480, space)))
    space += -100

text = 'Air 3'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space-50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

space += -100
temp_D = np.linspace(0.158,0.162,3)
temp_d = np.linspace(0.678,0.682,3)
for D in temp_D:
    for d in temp_d:
        cell = GC_PC.gc_PC_uniform(lib,filename0='GC_Air', D=D, d=d)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
        DEVICES.add(gdspy.CellReference(GC_line, (0, space)))
        space += -100
    space += -100

text = 'Air 4'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

dir_file = './data_apodized/Peorid_Diameter_min80_all.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180
d = temp['d_goal']*1e6 
cell = gc_PC_apodized(lib,'GC_Air_PC_Apodized', D2, d)
GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
DEVICES.add(gdspy.CellArray(GC_line, 1, 3, [0,-100], (0, space)))


space += -2500

text = 'SiO2 1'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

# load data for Air
filename = './data_apodized/apod_2D_params_SiO2_8Deg.txt'
data = readParameters(filename)

for complement in [0, 0.005, -0.005]:
    data_mod = list(np.array(data) + complement)
    cellname = 'GC_SiO2_Apodized_8Deg_' + str(int(complement*1e3))
    # create the rect grating for Air
    GC_rect_Apodized_Air = lib.new_cell(cellname)
    gc_rect(GC_rect_Apodized_Air, data)
    GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_rect_Apodized_Air)
    DEVICES.add(gdspy.CellReference(GC_line, (0, space)))
    space += -100

text = 'SiO2 2'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space-50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

space += -100
for complement in [0, 0.005, -0.005]:
    data_mod = list(np.array(data) + complement)
    cellname = 'GC_SiO2_Apodized_8Deg_focusing_' + str(int(complement*1e3))
    # create the rect grating for Air
    GC_focusing_Apodzied_Air = lib.new_cell(cellname)
    gc_focusing(GC_focusing_Apodzied_Air, data)
    GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_focusing_Apodzied_Air, l = 1160)
    DEVICES.add(gdspy.CellReference(GC_line, (-480, space)))
    space += -100

text = 'SiO2 3'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space-50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

space += -100
temp_D = np.linspace(0.163,0.167,3)
temp_d = np.linspace(0.698,0.702,3)
for D in temp_D:
    for d in temp_d:
        cell = GC_PC.gc_PC_uniform(lib,filename0='GC_SiO2', D=D, d=d)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
        DEVICES.add(gdspy.CellReference(GC_line, (0, space)))
        space += -100
    space += -100

text = 'SiO2 4'
com = lib.new_cell(text)
com.add(gdspy.Text(text, 40, (0, space+50), **ld_fulletch))
ref = gdspy.CellReference(com)
DEVICES.add(ref)

dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180
d = temp['d_goal']*1e6 
cell = gc_PC_apodized(lib,'GC_SiO2_PC_Apodized', D2, d)
GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
DEVICES.add(gdspy.CellArray(GC_line, 1, 3, [0,-100], (0, space)))

CELL = lib.new_cell('Devices')
CELL.add(gdspy.CellArray(DEVICES, 2, 1, [1500,0], (0, 0)))
lib.write_gds("GC_RPC.gds")

