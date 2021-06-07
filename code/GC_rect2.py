import numpy as np
import gdspy
import scipy.io as scio

def gc_rect(cell, pa):
    w_wg = 0.5
    w_etch = 3
    w = 10
    l_grating = 500
    xp = -l_grating - 6

    i=0
    while i<len(pa):
        a =  float(pa[i])
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

def gc_focusing(cell, pa):
    w_wg = 0.5
    w_etch = 3
    xp = 12
    GC_theta = 23/180*np.pi
    GC_theta2 = 20/180*np.pi
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
            number_of_points=128,
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
    w_wg = 0.5
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

def gc_line(cell, gc, origin=(0,0)):
    w_wg = 0.5
    l = 200
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (l+origin[0], origin[1]), rotation=180))
    path_connect = gdspy.Path(w_wg)
    path_connect.segment(l)
    path_connect2 = gdspy.Path(w_wg+6)
    path_connect2.segment(l)
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor')
    cell.add(path_connect_positive)
    return cell

def generator_parameters(pitch, ff, num_pitch):
    pa = [0]*num_pitch*2
    for i in range(num_pitch):
        pa[2*i] = round(pitch*(1-ff), 3)
        pa[2*i+1] = round(pitch*ff, 3)
    return pa

lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
DEVICES = lib.new_cell("DEVICES")

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

# parameter 1
ff = 0.616
pa = generator_parameters(0.873, ff, 30)
# single gc
lineGrating = lib.new_cell("GC_rect_"+str(ff))
gc_rect(lineGrating, pa)
focusGrating = lib.new_cell("GC_focusing_"+str(ff))
gc_focusing(focusGrating, pa)
# gc for FA
GC_foucus_FA = gc_FA(lib.new_cell("GC_fousing_FA"+str(ff)), focusGrating)
GC_rect_FA = gc_FA(lib.new_cell("GC_rect_FA"+str(ff)), lineGrating)
# gc for line
GC_foucus_line = gc_line(lib.new_cell("GC_foucus_line"+str(ff)), focusGrating)
GC_rect_line = gc_line(lib.new_cell("GC_rect_line"+str(ff)), lineGrating)
# Assemble
DEVICES.add(gdspy.CellArray(GC_foucus_FA, 1, 3, [1, 200]))
DEVICES.add(gdspy.CellArray(GC_rect_FA, 1, 3, [1, 200], origin=(650, 0)))
DEVICES.add(gdspy.CellArray(GC_foucus_line, 1, 3, [1, 100], origin=(800, -127)))
DEVICES.add(gdspy.CellArray(GC_rect_line, 1, 3, [1, 100], origin=(1300, 130)))

# parameter 1
ff = 0.5
pa = generator_parameters(0.873, ff, 30)
# single gc
lineGrating = lib.new_cell("GC_rect_"+str(ff))
gc_rect(lineGrating, pa)
focusGrating = lib.new_cell("GC_focusing_"+str(ff))
gc_focusing(focusGrating, pa)
# gc for FA
GC_foucus_FA = gc_FA(lib.new_cell("GC_fousing_FA"+str(ff)), focusGrating)
GC_rect_FA = gc_FA(lib.new_cell("GC_rect_FA"+str(ff)), lineGrating)
# gc for line
GC_foucus_line = gc_line(lib.new_cell("GC_foucus_line"+str(ff)), focusGrating)
GC_rect_line = gc_line(lib.new_cell("GC_rect_line"+str(ff)), lineGrating)
# Assemble
DEVICES.add(gdspy.CellArray(GC_foucus_FA, 1, 3, [1, 200],origin=(0, 600+0)))
DEVICES.add(gdspy.CellArray(GC_rect_FA, 1, 3, [1, 200], origin=(650, 600+0)))
DEVICES.add(gdspy.CellArray(GC_foucus_line, 1, 3, [1, 100], origin=(800, 600+-127)))
DEVICES.add(gdspy.CellArray(GC_rect_line, 1, 3, [1, 100], origin=(1300, 600+130)))

lib.write_gds("test.gds")

