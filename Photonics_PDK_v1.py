import numpy as np
import gdspy

layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 3}
ld_heater = {"layer": 2, "datatype": 1}
ld_wire = {"layer": 3, "datatype": 1}

ld_wg = {"layer": 100, "datatype": 1}
ld_cld = {"layer": 100, "datatype": 2}

info_wg = {"w_wg":0.5, "w_etch": 3}

def gc_rect(cell, pa, w_gc=12, w_wg=0.5, w_etch=3):
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

def gc_focusing(lib, cellname, pa, xp=22, theta=25, w_wg=0.5, w_etch=3):
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

def gc_focusing_PC(lib, filename0 ="GC", xp=14, theta=25, a=0.23, D=0.150, d=0.665, period_num=29, w_wg=0.5, w_etch=3):
    """
    cell: cell in Gdspy \n
    pa: parameters for grating coupler \n
    xp: the start position of pa \n
    theta: the angle of GC \n
    w_gc: width of grating coupler \n
    w_wg: width of waveguide\n
    w_etch: width of etch
    """
    # xp is the length of taper
    GC_theta = (theta+3)/180*np.pi
    GC_theta2 = theta/180*np.pi
    i = 0
    D_hole = 0.165
    a_hole = a

    # create the main body of phtonic crystal grating coupler
    d_all = np.ones(period_num)*d
    D_all = np.ones(period_num)*D
    # name the cell that include the grating
    filename = filename0 + "_a"+str(int(a*1e3)) +"_D"+str(int(D*1e3)) +"_d"+str(np.around(d*1e3,0).astype(int)) +"_wg"+ str(int(w_wg*1000))
    grating = lib.new_cell(filename)
    
    for ii in range(period_num):
        # this is for a variable period
        if ii == 0:
            x_start = -xp
        else:
            x_start += -d_all[ii]
        
        # create the cell for reference
        D_temp = D_all[ii]
        name_cell = "D"+str(int(D_temp*1e3))
        if name_cell not in lib.cells:
            circles = lib.new_cell(name_cell)
            circle = gdspy.Round((0, 0), D_temp/2, tolerance=0.0001, **ld_grating)
            circles.add(circle)
        else:
            Cell_all = lib.cells
            circles = Cell_all[name_cell]
        
        theta_delta = (a_hole*np.sqrt(3))/abs(x_start)
        num_y = np.floor(GC_theta2/theta_delta)*2
        if num_y % 2 == 0:
            num_y += 1

        # create the 3 column of hole
        for x_index in range(3):
            if x_index == 1:
                num_y = num_y + 1
            for y_index in range(int(num_y)):
                grating.add(gdspy.CellReference(circles,
                ((x_start + x_index*a/2)*np.cos(theta_delta*(y_index-(num_y - 1)/2)), (x_start + x_index*a/2)*np.sin(theta_delta*(y_index-(num_y - 1)/2)))))
            if x_index == 1:
                num_y = num_y - 1
            
    xp = abs(x_start)
    GC_theta = GC_theta2
    points = [(0, w_wg/2), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta)), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta) + w_etch), (0, w_wg/2 + w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    grating.add(poly)

    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
    grating.add(poly)
    return grating

def gc_focusing_PC_apodized(lib, D_all, d_all, filename0 ="FAGC", xp=14, theta=25, a=0.23, period_num=29, D_max=0.18, w_wg=0.5, w_etch=3):
    """
    cell: cell in Gdspy \n
    pa: parameters for grating coupler \n
    xp: the start position of pa \n
    theta: the angle of GC \n
    w_gc: width of grating coupler \n
    w_wg: width of waveguide\n
    w_etch: width of etch
    """
    # xp is the length of taper
    GC_theta = (theta+3)/180*np.pi
    GC_theta2 = theta/180*np.pi
    a_hole = a

    # create the main body of phtonic crystal grating coupler
    # d_all = np.ones(period_num)*d
    # D_all = np.ones(period_num)*D
    # name the cell that include the grating
    # filename = filename0 + "_a"+str(int(a*1e3)) +"_D"+str(int(D*1e3)) +"_d"+str(np.around(d*1e3,0).astype(int)) +"_wg"+ str(int(w_wg*1000)/)
    grating = lib.new_cell(filename0)
    
    for ii in range(period_num):
        # this is for a variable period
        if ii == 0:
            x_start = -xp
        else:
            x_start += -d_all[ii]
        
        # create the cell for reference
        D_temp = D_all[ii]
        if D_temp > D_max:
            D_temp = D_max
        name_cell = "D"+str(int(D_temp*1e3))
        if name_cell not in lib.cells:
            circles = lib.new_cell(name_cell)
            circle = gdspy.Round((0, 0), D_temp/2, tolerance=0.0001, **ld_grating)
            circles.add(circle)
        else:
            Cell_all = lib.cells
            circles = Cell_all[name_cell]
        
        theta_delta = (a_hole*np.sqrt(3))/abs(x_start)
        num_y = np.floor(GC_theta2/theta_delta)*2
        if num_y % 2 == 0:
            num_y += 1

        # create the 3 column of hole
        for x_index in range(3):
            if x_index == 1:
                num_y = num_y + 1
            for y_index in range(int(num_y)):
                grating.add(gdspy.CellReference(circles,
                ((x_start + x_index*a/2)*np.cos(theta_delta*(y_index-(num_y - 1)/2)), (x_start + x_index*a/2)*np.sin(theta_delta*(y_index-(num_y - 1)/2)))))
            if x_index == 1:
                num_y = num_y - 1
            
    xp = abs(x_start)
    GC_theta = GC_theta2
    points = [(0, w_wg/2), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta)), (-xp*np.cos(GC_theta), xp*np.sin(GC_theta) + w_etch), (0, w_wg/2 + w_etch)]
    poly = gdspy.Polygon(points, **ld_fulletch)
    grating.add(poly)

    poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
    grating.add(poly)
    return grating

def gc_FA(cell, gc, origin=(0,0), w_wg=0.5, w_etch=3):
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

    path_connect2 = gdspy.Path(w_wg+w_etch*2)
    path_connect2.segment(l_portIn)
    path_connect2.turn(10, "r")
    path_connect2.segment(107)
    path_connect2.turn(10, "r")
    path_connect2.segment(l_portOut)
    
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor', **ld_fulletch)
    cell.add(path_connect_positive)
    return cell

def gc_line(cell, gc, origin=(0,0), l=200, w_wg=0.5, w_etch=3):
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
    path_connect2 = gdspy.Path(w_wg+w_etch*2)
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

def gc_PC_apodized(lib, filename0, D, d_goal, period_num=29, l_taper_a=500, l_grating=30, w_gc=12, w_wg=0.5, w_etch=3, D_max=0.18):
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

def gc_PC_uniform(lib, filename0 ="UGC", a=0.23, D=0.150, d=0.665, period_num=29, w_gc=12, l_taper_a=500, l_grating=30, w_wg=0.5, w_etch=3 ):
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
    return cell

def convert_to_positive_resist2(cell, parts, buffer_radius=3):
    w_cut = 15
    l_cut= 15
    outer = gdspy.offset(parts, buffer_radius, join_first=True)

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
    outer2 = gdspy.boolean(outer, cut, 'not', **ld_cld)
    diff = gdspy.boolean(outer2, parts, 'not', **ld_fulletch)
    cell.add(outer2)
    cell.add(diff)
    return cell

def buffer(parts, buffer_radius=3):
    w_cut = 15
    l_cut= 15
    outer = gdspy.offset(parts, buffer_radius, join_first=True)

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
    outer2 = gdspy.boolean(outer, cut, 'not', **ld_cld)
    return outer2

def Scan_d(lib, Cell, D, d, cellname_prefix='UGC', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, type_GC='line'):
    temp_d =  np.linspace(d-step*n[0], d+step*n[1], n[0]+n[1]+1)
    pos_y = 0
    for d in temp_d:
        cell = gc_PC_uniform(lib,filename0=cellname_prefix, D=D, d=d, w_wg=w_wg, w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_trench(lib, Cell, para, cellname_prefix='AGC_R', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, type_GC='line'):
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
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), GC_rect_Apodized_Air, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), GC_rect_Apodized_Air, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_tooth(lib, Cell, para, cellname_prefix='AGC_R', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, type_GC='line'):
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
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), GC_rect_Apodized_Air, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), GC_rect_Apodized_Air, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_d_Apod(lib, Cell, D2, d, cellname_prefix='AGC_PC', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, type_GC='FA'):
    temp_complement=  offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = d
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_d' + str(round(complement*1e3)), D2, temp_para, w_wg=w_wg,  w_gc=w_gc)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_D_Apod(lib, Cell, D, d, cellname_prefix='AGC_PC', step=0.005, offset_scan=0, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, type_GC='FA',D_max=0.18):
    temp_complement=  offset_scan + np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    pos_y = 0
    para = D
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_D' + str(int(round(complement*1e3))), temp_para, d, w_wg=w_wg,  w_gc=w_gc, D_max=D_max)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_ltaper_focu(lib, Cell, para, l_taper, cellname_prefix='GC_foucusing', step=1, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=12, w_etch=3):
    temp_l_taper =  np.linspace(l_taper-step*n[0], l_taper+step*n[1], n[0]+n[1]+1)
    y_start = space
    for l in temp_l_taper:
        cell = gc_focusing(lib, cellname_prefix+'_lTaper'+str(round(l)), pa=para, xp=l, w_wg=w_wg,  w_gc=w_gc)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 1200, w_wg=w_wg, w_etch=w_etch)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]-500, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Scan_ltaper_UFocu(lib, Cell, D, d, xp, cellname_prefix='GC', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5, type_GC='line'):
    temp =  np.linspace(xp-step*n[0], xp+step*n[1], n[0]+n[1]+1)
    pos_y = 0
    for xp0 in temp:
        cell = gc_focusing_PC(lib, cellname_prefix+'_Xp'+str(round(xp0)), xp0, D=D, d=d, w_wg=w_wg)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
    return posi_end

def Scan_ltaper_AFocu(lib, Cell, D_all, d_all, xp, cellname_prefix='FAGC_PC', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5, type_GC='line'):
    temp =  np.linspace(xp-step*n[0], xp+step*n[1], n[0]+n[1]+1)
    pos_y = 0
    for xp0 in temp:
        cell = gc_focusing_PC_apodized(lib, D_all, d_all, cellname_prefix+'_Xp'+str(round(xp0)), xp0, w_wg=w_wg)
        if type_GC == 'line':
            GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200, w_wg=w_wg) 
        if type_GC == 'FA':
            GC_line = gc_FA(lib.new_cell(cell.name+"_FA"), cell, origin=(0,0), w_wg=w_wg)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+pos_y)))
        pos_y += -space
    posi_end = (origin[0]+0, origin[1]+pos_y-200)
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
def gene_heater(lib, cellName='Heater', w_heater=3, l_heater=200, w_CT=10, w_wire=20, w_wg=0.5, w_etch=3, type_layout='positive'):
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
    if type_layout == 'negative':
        Rect = gdspy.Rectangle((0, w_wg/2+w_etch), (l_Heater, w_wg/2), **ld_fulletch)
        cell.add(Rect)
        Rect = gdspy.Rectangle((0, -w_wg/2), (l_Heater, -w_wg/2-w_etch), **ld_fulletch)
        cell.add(Rect)
    if type_layout == 'positive':
        cell.add(wg_line(w_wg, l_Heater, w_etch=w_etch, type_layout='positive'))
        cell.add(buffer(wg_line(w_wg, l_Heater, w_etch=w_etch, type_layout='positive')))
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
def gene_ring(lib, cellName='Ring', radius_ring=10, gap=0.1, l_wg=40, w_wg=0.5):
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

# add MZM based on DC
def MZM_DC(lib, cell_Heater, cell_DC, cellName='MZM_DC', w_wg=0.5, N=2, w_etch_DC=3 ):
    bc = cell_DC.get_bounding_box()
    l_DC = bc[1][0] - bc[0][0]
    S_Port_DC = bc[1][1] - bc[0][1] - 2*w_etch_DC - w_wg
    bc = cell_Heater.get_bounding_box()
    l_Heater = bc[1][0] - bc[0][0]
    cell = lib.new_cell(cellName)
    cell.add(gdspy.CellArray(cell_DC, N+1, 1, (l_Heater+l_DC, 0)))
    cell.add(gdspy.CellArray(cell_Heater, N, 1, (l_Heater+l_DC, 0), (l_DC, 0)))
    for i in range(N):
        wg = wg_line(w_wg, w_etch_DC, ((l_DC+l_Heater)*i+l_DC, -S_Port_DC), l_Heater)
        cell.add(wg)
    return cell

# define the Waveguide
def wg_line(w_wg, l_wg, origin=(0,0), w_etch=3, type_layout='negative'):
    # add WG
    if type_layout == 'negative':
        Rect1 = gdspy.Rectangle((origin[0], origin[1]+w_wg/2+w_etch), (origin[0]+l_wg, origin[1]+w_wg/2), **ld_fulletch)
        Rect2 = gdspy.Rectangle((origin[0], origin[1]-w_wg/2), (origin[0]+l_wg, origin[1]-w_wg/2-w_etch), **ld_fulletch)
        return [Rect1, Rect2]
    else:
        Rect1 = gdspy.Rectangle((origin[0], origin[1]+w_wg/2), (origin[0]+l_wg, origin[1]-w_wg/2), **ld_wg)
        return Rect1
    

# define the 2X2 MMI or 1X2 MMI
def MMI(lib, cellName='MMI2X2', w_core=9, l_core=97, pos_taper=1.5, w_taper1=2.7, l_taper1=26, w_taper2=2.7, l_taper2=27, w_wg=0.5, type_layout='positive'):
    l_port = 5
    cell = lib.new_cell(cellName)
    if cellName == 'MMI2X2':
        # left taper up
        origin = (0, pos_taper)
        cell.add(wg_line(w_wg, l_port, origin=origin, type_layout='positive'))
        origin = (origin[0]+l_port, origin[1])
        pts = [(origin[0], origin[1]+w_wg/2), (origin[0]+l_taper1, origin[1]+w_taper1/2), (origin[0]+l_taper1, origin[1]-w_taper1/2), (origin[0], origin[1]-w_wg/2)]
        poly = gdspy.Polygon(pts, **ld_wg)
        cell.add(poly)
        # left taper down
        origin = (0, -pos_taper)
        cell.add(wg_line(w_wg, l_port, origin=origin, type_layout='positive'))
        origin = (origin[0]+l_port, origin[1])
        pts = [(origin[0], origin[1]+w_wg/2), (origin[0]+l_taper1, origin[1]+w_taper1/2), (origin[0]+l_taper1, origin[1]-w_taper1/2), (origin[0], origin[1]-w_wg/2)]
        poly = gdspy.Polygon(pts, **ld_wg)
        cell.add(poly)
    if cellName == 'MMI1X2':
        # left taper
        origin = (0, 0)
        cell.add(wg_line(w_wg, l_port, origin=origin, type_layout='positive'))
        origin = (origin[0]+l_port, origin[1])
        pts = [(origin[0], origin[1]+w_wg/2), (origin[0]+l_taper1, origin[1]+w_taper1/2), (origin[0]+l_taper1, origin[1]-w_taper1/2), (origin[0], origin[1]-w_wg/2)]
        poly = gdspy.Polygon(pts, **ld_wg)
        cell.add(poly)

    # core
    origin = (l_port+l_taper1, 0)
    cell.add(gdspy.Rectangle((origin[0], origin[1]+w_core/2), (origin[0]+l_core, origin[1]-w_core/2), **ld_wg))
    # right taper up
    origin = (origin[0]+l_core, origin[1]+pos_taper)
    pts = [(origin[0], origin[1]+w_taper2/2), (origin[0]+l_taper2, origin[1]+w_wg/2), (origin[0]+l_taper2, origin[1]-w_wg/2), (origin[0], origin[1]-w_taper2/2)]
    poly = gdspy.Polygon(pts, **ld_wg)
    cell.add(poly)
    origin = (origin[0]+l_taper2, origin[1])
    cell.add(wg_line(w_wg, l_port, origin=origin, type_layout='positive'))
    # right taper down
    origin = (l_port+l_taper1+l_core, -pos_taper)
    pts = [(origin[0], origin[1]+w_taper2/2), (origin[0]+l_taper2, origin[1]+w_wg/2), (origin[0]+l_taper2, origin[1]-w_wg/2), (origin[0], origin[1]-w_taper2/2)]
    poly = gdspy.Polygon(pts, **ld_wg)
    cell.add(poly)
    origin = (origin[0]+l_taper2, origin[1])
    cell.add(wg_line(w_wg, l_port, origin=origin, type_layout='positive'))
    if type_layout == 'negative':
        cell2 = lib.new_cell(cellName+'_')
        cell2 = convert_to_positive_resist(cell2, cell)
        lib.remove(cell)
        return cell2
    if type_layout == 'positive':
        cell.add(buffer(cell))
        return cell

# define the MZM based on MMI
def MZM_MMI(w_taper1, ltaper1, w_taper2, l_taper2):

    pass

def connect_zShape_(pos_start, pos_end, len_port=5, w=0.5, radius=10, layer=1, datatype=1):
    # Path defined by a sequence of points and stored as a GDSII path
    path = gdspy.FlexPath(
            [pos_start, (pos_start[0]+len_port+radius, pos_start[1]), (pos_start[0]+len_port+radius, pos_end[1]), pos_end], w, 0, ends="flush",
             layer=layer, datatype=datatype, bend_radius=radius, corners='circular bend', tolerance=0.001
    )
    return path

def connect_zShape(cell, pos_start, pos_end, len_port=5, w_wg=0.5, w_etch=3, radius=10, type_layout='positive'):
    path1 = connect_zShape_(pos_start, pos_end, len_port, w_wg, radius=radius, **ld_wg)
    path2 = connect_zShape_(pos_start, pos_end, len_port, w_wg+2*w_etch, radius=radius, **ld_cld)
    if type_layout=='positive':
        cell.add([path1, path2])
    if type_layout=='negative':
        cell.add(gdspy.boolean(path2, path1, 'xor', **ld_fulletch))
    return cell

def get_length(cell):
    bc = cell.get_bounding_box()
    l = bc[1][0] - bc[0][0]
    return l

# splitter 
def Splitter_12(lib, heater, mmi_12, mmi_22,  pos_y_heater=300, pos_taper_mmi_12=1.5, pos_taper_mmi_22=1.5, w_wg=0.5, w_etch=3, radius=10, len_port_ext=5):
    Splitter_1X2 = lib.new_cell('Splitter_1X2')

    len_heater = get_length(heater)
    len_mmi_12 = get_length(mmi_12)
    len_mmi_22 = get_length(mmi_22)
    out_1_mmi_22 = pos_taper_mmi_22
    out_2_mmi_22 = -out_1_mmi_22
    in_1_mmi_22 = out_1_mmi_22
    in_2_mmi_22 = out_2_mmi_22
    
    pos_x = 0 
    ## MMI 1X2
    Splitter_1X2.add(gdspy.CellReference(mmi_12))
    pos_x = len_mmi_12
    # wg
    connect_zShape(Splitter_1X2, (pos_x, pos_taper_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y_heater))
    connect_zShape(Splitter_1X2, (pos_x, -pos_taper_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater))
    # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    ## add  1st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # wg 
    connect_zShape(Splitter_1X2, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22))
    connect_zShape(Splitter_1X2, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22))
    # next
    pos_x += radius*2 + len_port_ext*2

    # ## the 2st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(mmi_22, (pos_x, 0)))
    pos_x += len_mmi_22
    connect_zShape(Splitter_1X2, (pos_x, out_1_mmi_22), (pos_x+2*radius+len_port_ext*2, pos_y_heater))
    connect_zShape(Splitter_1X2, (pos_x, out_2_mmi_22), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater))
    # # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    # ## add  2st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # # wg
    connect_zShape(Splitter_1X2, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22))
    connect_zShape(Splitter_1X2, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22))
    # # # next
    pos_x += radius*2 + len_port_ext*2

    # # the 3st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(mmi_22, (pos_x, 0)))

    # add commom GND
    # x_1 = len_mmi_22 + len_heater + (radius+len_port_ext)*2 - 15
    # len_GND = (radius+len_port_ext)*4 + len_mmi_22 + 31
    # path = gdspy.FlexPath([(x_1, pos_y_heater), (x_1+len_GND, pos_y_heater)], w_Al, 0, gdsii_path=True, **ld_wire)
    # Splitter_1X2.add(path)
    # x_1 =len_mmi_22 + len_heater + (radius+len_port_ext)*4 + len_mmi_22/2
    # path = gdspy.FlexPath([(x_1, pos_y_heater-80), (x_1, pos_y_heater+80)], 150, 0,  gdsii_path=True, **ld_wire)
    # Splitter_1X2.add(path)

    return Splitter_1X2

# splitter 
def Splitter_12_3Layers(lib, heater, mmi_12, mmi_22,  pos_y_heater=300, pos_taper_mmi_12=1.5, pos_taper_mmi_22=1.5, w_wg=0.5, w_etch=3, radius=10, len_port_ext=5):
    Splitter_1X2 = lib.new_cell('Splitter_1X2')

    len_heater = get_length(heater)
    len_mmi_12 = get_length(mmi_12)
    len_mmi_22 = get_length(mmi_22)
    out_1_mmi_22 = pos_taper_mmi_22
    out_2_mmi_22 = -out_1_mmi_22
    in_1_mmi_22 = out_1_mmi_22
    in_2_mmi_22 = out_2_mmi_22
    
    pos_x = 0 
    ## MMI 1X2
    Splitter_1X2.add(gdspy.CellReference(mmi_12))
    pos_x = len_mmi_12
    # wg
    connect_zShape(Splitter_1X2, (pos_x, pos_taper_mmi_12), (pos_x+2*radius+len_port_ext*2, pos_y_heater))
    connect_zShape(Splitter_1X2, (pos_x, -pos_taper_mmi_12), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater))
    # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    ## add  1st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # wg 
    connect_zShape(Splitter_1X2, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22))
    connect_zShape(Splitter_1X2, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22))
    # next
    pos_x += radius*2 + len_port_ext*2

    # ## the 2st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(mmi_22, (pos_x, 0)))
    pos_x += len_mmi_22
    connect_zShape(Splitter_1X2, (pos_x, out_1_mmi_22), (pos_x+2*radius+len_port_ext*2, pos_y_heater))
    connect_zShape(Splitter_1X2, (pos_x, out_2_mmi_22), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater))
    # # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    # ## add  2st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # # wg
    connect_zShape(Splitter_1X2, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22))
    connect_zShape(Splitter_1X2, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22))
    # # # next
    pos_x += radius*2 + len_port_ext*2

    # # the 3st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(mmi_22, (pos_x, 0)))
    pos_x += len_mmi_22
    connect_zShape(Splitter_1X2, (pos_x, out_1_mmi_22), (pos_x+2*radius+len_port_ext*2, pos_y_heater))
    connect_zShape(Splitter_1X2, (pos_x, out_2_mmi_22), (pos_x+2*radius+len_port_ext*2+len_heater, -pos_y_heater))
    # # next
    pos_y = pos_y_heater
    pos_x += radius*2 + len_port_ext*2

    # ## add  3st heater
    Splitter_1X2.add(gdspy.CellReference(heater, (pos_x, pos_y)))
    pos_x += len_heater
    # # wg
    connect_zShape(Splitter_1X2, (pos_x, pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_1_mmi_22))
    connect_zShape(Splitter_1X2, (pos_x, -pos_y_heater), (pos_x+2*radius+len_port_ext*2, in_2_mmi_22))
    # # # next
    pos_x += radius*2 + len_port_ext*2

    # # the 4st MMI 2X2
    Splitter_1X2.add(gdspy.CellReference(mmi_22, (pos_x, 0)))


    # add commom GND
    # x_1 = len_mmi_22 + len_heater + (radius+len_port_ext)*2 - 15
    # len_GND = (radius+len_port_ext)*4 + len_mmi_22 + 31
    # path = gdspy.FlexPath([(x_1, pos_y_heater), (x_1+len_GND, pos_y_heater)], w_Al, 0, gdsii_path=True, **ld_wire)
    # Splitter_1X2.add(path)
    # x_1 =len_mmi_22 + len_heater + (radius+len_port_ext)*4 + len_mmi_22/2
    # path = gdspy.FlexPath([(x_1, pos_y_heater-80), (x_1, pos_y_heater+80)], 150, 0,  gdsii_path=True, **ld_wire)
    # Splitter_1X2.add(path)

    return Splitter_1X2

def Splitter_tree(lib, num, heater, mmi_12, mmi_22,  pos_y_heater=150, pos_taper_mmi_12=1.5, pos_taper_mmi_22=1.5, w_wg=0.5, w_etch=3, radius=10, len_port_ext=5):
    
    Splitter_1X2 = Splitter_12_3Layers(lib, heater, mmi_12, mmi_22,  pos_y_heater, pos_taper_mmi_12, pos_taper_mmi_22, w_wg, w_etch, radius, len_port_ext)
    
    out_1_mmi_22 = pos_taper_mmi_22
    out_2_mmi_22 = -out_1_mmi_22

    ## define the splitter tree
    pos_x = 0
    pos_y = 0
    position_all = []
    len_splitter_1X2 = get_length(Splitter_1X2)
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
                connect_zShape(ST, (pos_x+len_splitter_1X2, pos_y+out_1_mmi_22), (pos_x+len_splitter_1X2+2*radius+len_port_ext*2, pos_y+2**(N-2-i)*space_y/2))
                connect_zShape(ST, (pos_x+len_splitter_1X2, pos_y+out_2_mmi_22), (pos_x+len_splitter_1X2+2*radius+len_port_ext*2, pos_y-2**(N-2-i)*space_y/2))
    return ST, position_all

__name__ = 'test_splitterTree'

if __name__ == '__main__':
    lib = gdspy.GdsLibrary( precision=1e-10)
    MMI(lib)
    gdspy.LayoutViewer()
    # name_gds = "test_MZM_DC.gds"
    # lib.write_gds(name_gds)
    # print(name_gds)

if __name__ == 'test_splitterTree':
    lib = gdspy.GdsLibrary( precision=1e-10)
    mmi_12 = MMI(lib, 'MMI1X2')
    mmi_22 = MMI(lib)
    heater = gene_heater(lib)
    # Splitter_12(lib, heater=heater, mmi_12=mmi_12, mmi_22=mmi_22)
    Splitter_tree(lib, 8, heater=heater, mmi_12=mmi_12, mmi_22=mmi_22, pos_y_heater=127)
    gdspy.LayoutViewer()
    name_gds = "test_ST.gds"
    lib.write_gds(name_gds)
    print(name_gds)