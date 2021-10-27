import numpy as np
import gdspy
import scipy.io as scio

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 3}

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

def gc_focusing_PC_P(lib, filename0 ="GC", xp=14, theta=25, a=0.23, D=0.150, d=0.665, period_num=29, w_wg=0.5, w_etch=3):
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
    GC_theta = theta/180*np.pi
    a_hole = a

    # create the main body of phtonic crystal grating coupler
    d_all = np.ones(period_num)*d
    D_all = np.ones(period_num)*D
    # name the cell that include the grating
    filename = filename0 + "_a"+str(int(a*1e3)) +"_D"+str(int(D*1e3)) +"_d"+str(np.around(d*1e3,0).astype(int)) +"_wg"+ str(int(w_wg*1000))
    grating = lib.new_cell(filename)
    
    cell = lib.new_cell('circles')
    for ii in range(period_num):
        # this is for a variable period
        if ii == 0:
            x_start = -xp
        else:
            x_start += -d_all[ii]
        
        # create the cell for reference

        D_temp = D_all[ii]
        D_temp = np.around(D_temp, 4)
        name_cell = "D"+str(int(D_temp*1e3))
        if name_cell not in lib.cells:
            circles = lib.new_cell(name_cell)
            circle = gdspy.Round((0, 0), D_temp/2, tolerance=0.0001, **ld_grating)
            circles.add(circle)
        else:
            Cell_all = lib.cells
            circles = Cell_all[name_cell]
        
        theta_delta = (a_hole*np.sqrt(3))/abs(x_start)
        num_y = np.floor(GC_theta/theta_delta)*2
        if num_y % 2 == 0:
            num_y += 1

        # create the 3 column of hole
        for x_index in range(3):
            if x_index == 1:
                num_y = num_y + 1
            for y_index in range(int(num_y)):
                cell.add(gdspy.CellReference(circles,
                ((x_start + x_index*a/2)*np.cos(theta_delta*(y_index-(num_y - 1)/2)), (x_start + x_index*a/2)*np.sin(theta_delta*(y_index-(num_y - 1)/2)))))
            if x_index == 1:
                num_y = num_y - 1
    
    circle = gdspy.Round((w_wg/np.tan(GC_theta)/2, 0), radius=abs(x_start)+10, initial_angle=np.pi-GC_theta, final_angle=np.pi+GC_theta, tolerance=0.0001)
    grating.add(circle)

    path = gdspy.Path(w_wg)
    path.segment(10)
    grating.add(path)

    grating = grating.add(gdspy.boolean(grating, cell, 'xor', precision=0.0001, layer=2))
    return grating

def gc_focusing_PC_apodized_P(lib, D, d, filename0 ="AGC_PC", xp=14, theta=25, a=0.23, period_num=29, w_wg=0.5, w_etch=3, D_max=0.18):
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
    GC_theta = theta/180*np.pi
    # create the main body of phtonic crystal grating coupler
    d_all = d
    D_all = D
    # name the cell that include the grating
    filename = filename0 +"_wg"+ str(int(w_wg*1000))

    grating = lib.new_cell(filename)
    
    cell = lib.new_cell('circles')
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
        
        theta_delta = (a*np.sqrt(3))/abs(x_start)
        num_y = np.floor(GC_theta/theta_delta)*2
        if num_y % 2 == 0:
            num_y += 1

        # create the 3 column of hole
        for x_index in range(3):
            if x_index == 1:
                num_y = num_y + 1
            for y_index in range(int(num_y)):
                cell.add(gdspy.CellReference(circles,
                ((x_start + x_index*a/2)*np.cos(theta_delta*(y_index-(num_y - 1)/2)), (x_start + x_index*a/2)*np.sin(theta_delta*(y_index-(num_y - 1)/2)))))
            if x_index == 1:
                num_y = num_y - 1
    
    circle = gdspy.Round((w_wg/np.tan(GC_theta)/2, 0), radius=abs(x_start)+10, initial_angle=np.pi-GC_theta, final_angle=np.pi+GC_theta, tolerance=0.0001)
    grating.add(circle)

    path = gdspy.Path(w_wg)
    path.segment(10)
    grating.add(path)

    grating = grating.add(gdspy.boolean(grating, cell, 'xor', precision=0.0001, layer=2))
    return grating

lib = gdspy.GdsLibrary( precision=1e-10)

kwargs = {'w_gc': 12, 'w_wg': 0.510}
layer_Mark = {"layer": 0, "datatype": 0}
ld_fulletch = {"layer": 1, "datatype": 1}

Die = lib.new_cell('Com_GC_PC')

# load data for SiO2
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)
D = temp['D']*1e6
d = temp['d_goal']*1e6 
D = np.reshape(D, -1)
d = np.reshape(d, -1)

cell = gc_focusing_PC(lib)
Die.add(gdspy.CellReference(cell))

# gdspy.LayoutViewer(lib, cell,depth=3)
lib.write_gds('Com_GC.gds')