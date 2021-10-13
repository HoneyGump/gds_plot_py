import numpy as np
import gdspy

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 3}
ld_heater = {"layer": 2, "datatype": 1}
ld_wire = {"layer": 3, "datatype": 1}

info_wg = {"w_wg":0.5, "w_etch": 3}

def gc_rect(cell, pa, w_gc=10, w_wg=0.5, w_etch=3):
    """
    cell: cell in Gdspy \n
    pa: parameters for grating coupler \n
    w_gc: width of grating coupler \n
    w_wg: width of waveguide\n
    w_etch: width of etch
    """
    l_grating = 500
    xp = -l_grating - 6 # xp is the position of x
    i=0
    while i<len(pa):
        a =  float(pa[i]) # here a is the trench that will be etched, b is the teeth
        b =  float(pa[i+1])

        points = [(xp, -w_gc/2), (xp, w_gc/2), (xp-a, w_gc/2), (xp-a, -w_gc/2)]
        poly = gdspy.Polygon(points, **ld_fulletch) 
        cell.add(poly)

        pitch = a + b
        xp += -pitch
        i += 2
    
    points = [(0, w_wg/2), (-l_grating, w_gc/2), (xp-10, w_gc/2), (xp-10, w_gc/2+w_etch), (-l_grating, w_gc/2+w_etch), (0, w_wg/2+w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    cell.add(poly)

    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
    cell.add(poly)
    return cell

def gc_focusing(lib, cellname, pa, xp=22, theta=25, w_gc=10, w_wg=0.5, w_etch=3):
    """
    cell: cell in Gdspy \n
    pa: parameters for grating coupler \n
    xp: the start position of pa \n
    theta: the angle of GC \n
    w_gc: width of grating coupler \n
    w_wg: width of waveguide\n
    w_etch: width of etch
    """
    cell = lib.new_cell(cellname)
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
    return cell

def gc_FA(cell, gc, origin=(0,0), w_gc=10, w_wg=0.5, w_etch=3):
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (origin[0],-127)))
    
    l_portIn = 400
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
    
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor', **ld_fulletch)
    cell.add(path_connect_positive)
    return cell

def gc_line(cell, gc, origin=(0,0), l=200, w_gc=10, w_wg=0.5, w_etch=3):
    """
    cell: cell in Gdspy \n
    
    w_gc: width of grating coupler \n
    w_wg: width of waveguide\n
    w_etch: width of etch
    """
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (l+origin[0], origin[1]), rotation=180))
    path_connect = gdspy.Path(w_wg)
    path_connect.segment(l)
    path_connect2 = gdspy.Path(w_wg+6)
    path_connect2.segment(l)
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor',layer=1, datatype=1)
    cell.add(path_connect_positive)
    return cell

def generator_parameters(pitch, ff, num_pitch, w_gc=10, w_wg=0.5, w_etch=3):
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

def gc_PC_apodized(lib, filename0, D, d_goal, period_num=29, l_taper_a=500, l_grating=30, w_gc=10, w_wg=0.5, w_etch=3, D_max=0.18):
    a = 0.23
    w_gc = w_gc
    num_y = np.floor(w_gc/(a*np.sqrt(3)))
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
        D_temp = np.around(D_temp, 4)
        if D_temp > D_max:
            D_temp = D_max
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
            num_y = np.floor(w_gc/pitch_y)
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

def gc_PC_uniform(lib, filename0 ="GC", a=0.23, D=0.150, d=0.665, period_num=29, w_gc=10, l_taper_a=500, l_grating=30, w_wg=0.5, w_etch=3 ):
    """ a is the length of the lattice \n
        D is the diameter of the hole \n
        d is the peorid of the gratings.
        """

    # create the main body of phtonic crystal grating coupler
    d_all = np.ones(period_num)*d
    D_all = np.ones(period_num)*D
    # name the cell that include the grating
    filename = filename0 + "_a"+str(int(a*1e3)) +"_D"+str(int(D*1e3)) +"_d"+str(np.around(d*1e3,0).astype(int)) +"_wg"+ str(int(w_wg*1000))
    grating = lib.new_cell(filename)

    num_y = np.floor(w_gc/(a*np.sqrt(3)))
    pitch_y = a*np.sqrt(3) # pitch in the y direction

    for ii in range(period_num):
        # this is for a variable period
        if ii == 0:
            x_start = -l_taper_a - 6
        else:
            x_start += -d_all[ii]
        
        # create the cell for reference
        D_temp = D_all[ii]
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
            num_y = np.floor(w_gc/(a*np.sqrt(3)))
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

            isTaper_b = 0
            if isTaper_b == 1:
                l_taper_b = 100
                points = [(l_taper_a+l_grating, w_gc/2), (l_taper_a+l_grating+l_taper_b, 0.05), (l_taper_a+l_grating+l_taper_b, 0.05+w_etch), (l_taper_a+l_grating, w_gc/2+w_etch)]
                poly = gdspy.Polygon(points, **ld_fulletch)
                grating.add(poly)

                poly = gdspy.Polygon(points, **ld_fulletch).mirror((0, 0), (1, 0))
                grating.add(poly)
    return grating

def coulper_coupler(lib, grating, w_wg=0.5, w_etch=3, l_wg=100):
    GC = lib.new_cell("GC")
    # create the cell: waveguides
    wg = lib.new_cell('waveguides'+str(int(w_wg*1000)))
    points = [(0, w_wg/2), (l_wg, w_wg/2), (l_wg, w_wg/2+w_etch), (0, w_wg/2+w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    wg.add(poly)
    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0, 0), (1, 0))
    wg.add(poly)
    GC.add(gdspy.CellReference(grating, origin=(0,0), rotation=180))
    GC.add(gdspy.CellReference(wg, origin=(0,0), rotation=0))
    GC.add(gdspy.CellReference(grating, origin=(l_wg,0), rotation=0))

def convert_to_positive_resist(cell, parts, buffer_radius=3):
    w_cut = 15
    l_cut= 15
    outer = gdspy.offset(parts, buffer_radius, join_first=True)
    diff = gdspy.boolean(outer, parts, 'not')

    x_max = 1
    x_min = 0
    if isinstance(parts,list):
        for onePart in parts:
            [[x_min_temp, __], [x_max_temp, __]] = onePart.get_bounding_box()
            if x_max_temp > x_max:
                x_max = x_max_temp
            if x_min_temp < x_min:
                x_min = x_min_temp
    else:
        [[x_min, __], [x_max, __]] = parts.get_bounding_box()
    points = [(x_min, w_cut), (x_min, -w_cut), (x_min-l_cut, -w_cut), (x_min-l_cut, w_cut)]
    poly1 = gdspy.Polygon(points)
    points = [(x_max, w_cut), (x_max, -w_cut), (x_max+l_cut, -w_cut), (x_max+l_cut, w_cut)]
    poly2= gdspy.Polygon(points)
    cut = gdspy.boolean(poly1, poly2, 'or')
    diff = gdspy.boolean(diff, cut, 'not', layer=1, datatype=1)
    cell.add(diff)

def Scan_d(lib, Cell, D, d, cellname_prefix='GC', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, type_GC='line'):
    temp_d =  np.linspace(d-step*n[0], d+step*n[1], n[0]+n[1]+1)
    pos_y = 0
    for d in temp_d:
        cell = gc_PC_uniform(lib,filename0=cellname_prefix, D=D, d=d, w_wg=w_wg, w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg, w_gc=w_gc) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg, w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_trench(lib, Cell, para, cellname_prefix='GC_Apodized', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, type_GC='line'):
    temp_complement = offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = np.array(para)
    temp_para = np.array(para)
    for complement in temp_complement:
        for index_para in range(len(para)):
            if index_para % 2 == 0:
                temp_para[index_para] = para[index_para] + complement
            else:
                temp_para[index_para] = para[index_para] - complement
        temp_para = list(temp_para)
        cellname = cellname_prefix + '_Trench' + str(round(complement*1e3))
        
        # create the rect grating for Air
        GC_rect_Apodized_Air = lib.new_cell(cellname)
        cell=GC_rect_Apodized_Air
        gc_rect(GC_rect_Apodized_Air, temp_para, w_wg=w_wg,  w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), GC_rect_Apodized_Air, l = 200, w_wg=w_wg, w_gc=w_gc) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), GC_rect_Apodized_Air, origin=(0,0), w_wg=w_wg, w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_tooth(lib, Cell, para, cellname_prefix='GC_Apodized', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, type_GC='line'):
    temp_complement =  offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = np.array(para)
    temp_para = np.array(para)
    for complement in temp_complement:
        for index_para in range(len(para)):
            if index_para % 2 != 0:
                temp_para[index_para] = para[index_para] + complement
        temp_para = list(temp_para)
        cellname = cellname_prefix + '_Tooth' + str(round(complement*1e3))
        
        # create the rect grating for Air
        GC_rect_Apodized_Air = lib.new_cell(cellname)
        cell = GC_rect_Apodized_Air
        gc_rect(GC_rect_Apodized_Air, temp_para, w_wg=w_wg,  w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), GC_rect_Apodized_Air, l = 200, w_wg=w_wg, w_gc=w_gc) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), GC_rect_Apodized_Air, origin=(0,0), w_wg=w_wg, w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_d_Apod(lib, Cell, D2, d, cellname_prefix='GC_PC_APodized', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, type_GC='FA'):
    temp_complement=  offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = d
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_d' + str(round(complement*1e3)), D2, temp_para, w_wg=w_wg,  w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg, w_gc=w_gc) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg, w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_D_Apod(lib, Cell, D, d, cellname_prefix='GC_PC_APodized', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, type_GC='FA',D_max=0.18):
    temp_complement=  offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = D
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_D' + str(int(round(complement*1e3))), temp_para, d, w_wg=w_wg,  w_gc=w_gc, D_max=D_max)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg, w_gc=w_gc) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg, w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_ltaper_focu(lib, Cell, para, l_taper, cellname_prefix='GC_foucusing', step=1, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10, w_etch=3):
    temp_l_taper =  np.linspace(l_taper-step*n[0], l_taper+step*n[1], n[0]+n[1]+1)
    y_start = space
    for l in temp_l_taper:
        cell = gc_focusing(lib, cellname_prefix+'_lTaper'+str(round(l)), pa=para, xp=l, w_wg=w_wg,  w_gc=w_gc)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 1200, w_wg=w_wg,  w_gc=w_gc)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]-500, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Mark_crossmark(lib, w=20, l=300, layer=1, datatype=1):
    mark = lib.new_cell("CrossMark")
    points = [(-l/2, w/2), (l/2, w/2), (l/2, -w/2), (-l/2, -w/2)]
    Poly1 = gdspy.Polygon(points, layer=layer, datatype=datatype)
    mark.add(Poly1)
    points = [(-w/2, l/2), (-w/2, -l/2), (w/2, -l/2), (w/2, l/2)]
    Poly1 = gdspy.Polygon(points, layer=layer, datatype=datatype)
    mark.add(Poly1)
    return mark

def get_ring(cell, origin, w, l, gap, radius, pos_wg, layer, datatype):
    pos_x = 0
    pos_y = 0
    pts = [(pos_x, pos_y+w/2), (pos_x+l, pos_y+w/2), (pos_x+l, pos_y-w/2), (pos_x, pos_y-w/2)]
    poly = gdspy.Polygon(pts, layer=layer, datatype=datatype)
    cell.add(poly)
    ring = gdspy.Round(center=origin, radius=radius+w/2, inner_radius=radius-w/2, layer=layer, datatype=datatype)
    cell.add(ring)
    pos_x = 0
    pos_y = pos_wg
    pts = [(pos_x, pos_y+w/2), (pos_x+l, pos_y+w/2), (pos_x+l, pos_y-w/2), (pos_x, pos_y-w/2)]
    poly = gdspy.Polygon(pts, layer=layer, datatype=datatype)
    cell.add(poly)
    return cell

def get_Ring(layer, datatype):
    w_wg = 0.5
    w_cld = 6.5
    radius = 1000
    l = 2*radius
    gap = 0.1
    origin = (l/2, -radius-gap-w_wg)
    pos_wg = -(radius*2 + gap*2 + 2*w_wg)
    lib = gdspy.GdsLibrary( precision=1e-10)
    cell1 = lib.new_cell('Devices1')
    cell2 = lib.new_cell('Devices2')
    cell = lib.new_cell('Ring')
    get_ring(cell1, origin=origin, w=w_wg, l=l, radius=radius, gap=gap, pos_wg=pos_wg, layer=1, datatype=1)
    get_ring(cell2, origin=origin, w=w_cld, l=l, radius=radius, gap=gap, pos_wg=pos_wg, layer=1, datatype=1)
    cell.add(gdspy.boolean(gdspy.CellReference(cell1), gdspy.CellReference(cell2), 'xor', layer=layer, datatype=datatype))
    return cell

def Path2WG(pts, w_wg, w_cld, layer, datatype):
    path1 = gdspy.FlexPath(pts, w_wg, corners='circular bend', bend_radius=10)
    path2 = gdspy.FlexPath(pts, w_cld, corners='circular bend', bend_radius=10)
    path = gdspy.boolean(path1, path2, 'xor', layer=layer, datatype=datatype)
    return path

# define  heater
def gene_heater(lib, cellName='Heater', w_heater=3, l_heater=200, w_CT=10, w_wire=20, w_wg=0.45, w_etch=3):
    # l_heater2 = l_heater - 100
    # w_heater = 3
    # w_CT = 10
    # w_wire = w_CT*2
    # w_wg = 0.45
    # w_etch = 3
    l_port = 20
    l_Heater = l_heater + 2*l_port
    cell = lib.new_cell(cellName)
    # add middle long rect
    heater = gdspy.Rectangle((l_port, w_heater/2), (l_port+l_heater, -w_heater/2), **ld_heater)
    cell.add(heater)
    # add left rect and wire
    heater = gdspy.Rectangle((l_port+-w_CT/2, w_CT/2), (l_port+w_CT/2, -w_CT/2), **ld_heater)
    cell.add(heater)
    heater = gdspy.Rectangle((l_port+-w_wire/2, w_wire/2), (l_port+w_wire/2, -w_wire/2), **ld_wire)
    cell.add(heater)
    # add right rect and wire
    heater = gdspy.Rectangle((l_port+l_heater-w_CT/2, w_CT/2), (l_port+l_heater+w_CT/2, -w_CT/2), **ld_heater)
    cell.add(heater)
    heater = gdspy.Rectangle((l_port+l_heater-w_wire/2, w_wire/2), (l_port+l_heater+w_wire/2, -w_wire/2), **ld_wire)
    cell.add(heater)
    # add WG
    Rect = gdspy.Rectangle((0, w_wg/2+w_etch), (l_Heater, w_wg/2), **ld_fulletch)
    cell.add(Rect)
    Rect = gdspy.Rectangle((0, -w_wg/2), (l_Heater, -w_wg/2-w_etch), **ld_fulletch)
    cell.add(Rect)

    return cell

class Ring_4port(object):
    def __init__(self, layer, datatype):
        self.layer = layer
        self.datatype= datatype

    def place_ring(self, l):
        w_wg = 0.5
        w_cld = 6.5
        radius = 1000
        # l = 2*radius
        gap = 0.1
        origin = (l/2, -radius-gap-w_wg)
        pos_wg = -(radius*2 + gap*2 + 2*w_wg)
        lib = gdspy.GdsLibrary( precision=1e-10)
        cell1 = lib.new_cell('Devices1')
        cell2 = lib.new_cell('Devices2')
        cell = lib.new_cell('Ring')
        get_ring(cell1, origin=origin, w=w_wg, l=l, radius=radius, gap=gap, pos_wg=pos_wg, layer=1, datatype=1)
        get_ring(cell2, origin=origin, w=w_cld, l=l, radius=radius, gap=gap, pos_wg=pos_wg, layer=1, datatype=1)
        cell.add(gdspy.boolean(gdspy.CellReference(cell1), gdspy.CellReference(cell2), 'xor', layer=self.layer, datatype=self.datatype))
        w = 3
        heater = gdspy.Round(origin, radius+w/2, radius-w/2, 135*np.pi/180, 225*np.pi/180, layer=2, datatype=1)
        cell.add(heater)
        heater = gdspy.Round(origin, radius+w/2, radius-w/2, -45*np.pi/180, 45*np.pi/180, layer=2, datatype=1)
        cell.add(heater)
        self.port = [(0,0), (0, pos_wg), (l, 0), (l, pos_wg)]
        return cell

# define Single Ring
def gene_ring(lib, cellName='Ring', radius_ring=10, gap=0.1, l_wg=40, w_wg=0.45):
    ring = lib.new_cell(cellName+str(int(radius_ring))+'_gap'+str(int(gap*1000)))
    points = [(0, -w_wg/2), (l_wg, -w_wg/2), (l_wg, w_wg/2), (0, w_wg/2)]
    poly = gdspy.Polygon(points)
    arc = gdspy.Round(
        (l_wg/2, -gap-w_wg-radius_ring),
        radius_ring+w_wg/2,
        inner_radius=radius_ring-w_wg/2 ,
        tolerance=0.001,
    )
    convert_to_positive_resist(ring, [poly, arc], buffer_radius=3)

    return ring

# define direction coupler
def DC(lib, cellName='DC', l_DC=20, spacing=0.6, radius_bend=10, l_ver=10, w_wg=0.5):
    l_PortIn = 10
    cell = lib.new_cell(cellName)
    
    path_dc = gdspy.Path(w_wg, (0,0))
    path_dc.segment(l_PortIn)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_DC)
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
    path_dc.segment(l_DC)
    path_dc.turn(radius_bend,'r')
    path_dc.segment(l_ver)
    path_dc.turn(radius_bend,'l')
    path_dc.segment(l_PortIn)
    cell.add(path_dc)

    return cell

# define direction coupler2
def DC2(lib, cellName='DC', l_DC=20, spacing=0.6, radius_bend=10, l_ver=10, w_wg=0.5, w_etch=3 ):
    cell1 = DC(lib, 'temp1_'+cellName, l_DC, spacing, radius_bend, l_ver, w_wg)
    cell2 = DC(lib, 'temp2_'+cellName, l_DC, spacing, radius_bend, l_ver, w_wg+2*w_etch)
    lib.remove(cell1)
    lib.remove(cell2)
    cell = lib.new_cell(cellName)
    poly = gdspy.boolean(cell1, cell2, 'xor', **ld_fulletch)
    cell.add(poly)
    return cell

if __name__ == '__main__':
    lib = gdspy.GdsLibrary( precision=1e-10)
    DC2(lib, 'Ring')
    gdspy.LayoutViewer()
    # test = Ring_4port(1,1)
    # cell.add(test.place_ring())
    # print(test.port)
    lib.write_gds('test_ring.gds')