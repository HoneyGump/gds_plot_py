import numpy as np
import gdspy

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

def gc_rect(cell, pa, w=10, w_wg=0.5, w_etch=3):
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

def gc_focusing(cell, pa,  xp=22, theta=25, w=10, w_wg=0.5, w_etch=3):
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

def gc_FA(cell, gc, origin=(0,0), w=10, w_wg=0.5, w_etch=3):
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

def gc_line(cell, gc, origin=(0,0), l=200, w=10, w_wg=0.5, w_etch=3):
    cell.add(gdspy.CellReference(gc, origin))
    cell.add(gdspy.CellReference(gc, (l+origin[0], origin[1]), rotation=180))
    path_connect = gdspy.Path(w_wg)
    path_connect.segment(l)
    path_connect2 = gdspy.Path(w_wg+6)
    path_connect2.segment(l)
    path_connect_positive = gdspy.boolean(path_connect, path_connect2,'xor',layer=1, datatype=1)
    cell.add(path_connect_positive)
    return cell

def generator_parameters(pitch, ff, num_pitch, w=10, w_wg=0.5, w_etch=3):
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

def gc_PC_apodized(lib, filename0, D, d_goal, period_num=29, l_taper_a=500, l_grating=30, w=10, w_wg=0.5, w_etch=3):
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

def gc_PC_uniform(lib, filename0 ="GC", a=0.23, D=0.150, d=0.665, period_num=29, w_gc=10, l_taper_a=500, l_grating=30, w_wg=0.5, w_etch=3 ):
    """ a is the length of the lattice \n
        D is the diameter of the hole \n
        d is the peorid of the gratings.
        """

    ld_fulletch = {"layer": 1, "datatype": 1}
    ld_grating = {"layer": 1, "datatype": 1}

    # create the main body of phtonic crystal grating coupler
    d_all = np.ones(period_num)*d
    D_all = np.ones(period_num)*D
    # name the cell that include the grating
    filename = filename0 + "_a"+str(int(a*1e3)) +"_D"+str(int(D*1e3)) +"_d"+str(int(d*1e3)) +"_wg"+ str(int(w_wg*1000))
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
    ld_fulletch = {"layer": 1, "datatype": 1}
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

def Scan_d(lib, Cell, D, d, cellname_prefix='GC', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5,  w_gc=10):
    temp_d =  np.linspace(d-step*n[0], d+step*n[1], n[0]+n[1]+1)
    y_start = space
    for d in temp_d:
        cell = gc_PC_uniform(lib,filename0=cellname_prefix+'_Air', D=D, d=d, w_wg=w_wg, w_gc=w_gc)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Scan_trench(lib, Cell, para, cellname_prefix='GC_Apodized', step=0.005, n=(3,4), origin=(0,0), space=100, w_wg=0.5, w_gc=10):
    temp_complement=  np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    y_start = space
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
        gc_rect(GC_rect_Apodized_Air, temp_para, w_wg=w_wg,  w=w_gc)
        GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_rect_Apodized_Air)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Scan_tooth(lib, Cell, para, cellname_prefix='GC_Apodized',step=0.005, n=(3,4), origin=(0,0), space=100):
    temp_complement=  np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    y_start = space
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
        gc_rect(GC_rect_Apodized_Air, temp_para)
        GC_line = gc_line(lib.new_cell(cellname+"_Line"), GC_rect_Apodized_Air)
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Scan_d_Apod(lib, Cell, D2, d, cellname_prefix='GC_PC_APodized', step=0.005, n=(3,4), origin=(0,0), space=100):
    temp_complement=  np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    y_start = space
    para = d
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_d' + str(round(complement*1e3)), D2, temp_para)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Scan_D_Apod(lib, Cell, D, d, cellname_prefix='GC_PC_APodized', step=0.005, n=(3,4), origin=(0,0), space=100):
    temp_complement=  np.linspace(-step*n[0], step*n[1], n[0]+n[1]+1)
    y_start = space
    para = D
    # print(para)
    for complement in temp_complement:
        temp_para = para + complement
        # print(temp_para)
        cell = gc_PC_apodized(lib, cellname_prefix+'_D' + str(round(complement*1e3)), temp_para, d)
        GC_line = gc_line(lib.new_cell(cell.name+"_Line"), cell, l = 200) 
        Cell.add(gdspy.CellReference(GC_line, (origin[0]+0, origin[1]+space-y_start)))
        space += -100
    posi_end = (origin[0]+0, origin[1]+space-200)
    return posi_end

def Mark_crossmark(lib, w=20, l=300):
    mark = lib.new_cell("CrossMark")
    points = [(-l/2, w/2), (l/2, w/2), (l/2, -w/2), (-l/2, -w/2)]
    Poly1 = gdspy.Polygon(points, layer=1, datatype=1)
    mark.add(Poly1)
    points = [(-w/2, l/2), (-w/2, -l/2), (w/2, -l/2), (w/2, l/2)]
    Poly1 = gdspy.Polygon(points, layer=1, datatype=1)
    mark.add(Poly1)
    return mark

if __name__ == '__main__':
    lib = gdspy.GdsLibrary( precision=1e-10)
    mark = Mark_crossmark(lib)
    cell = lib.new_cell('Devices')
    refe = gdspy.CellArray(mark, 2, 2, [1000, 1000], (-500, 500))
    cell.add(refe)
    lib.write_gds('test_mark2.gds')

