import numpy as np
import gdspy

def gratingCoupler_tradition(lib, a=0.23, D=0.150, d=0.665, period_num=29, w_gc=10, l_taper_a=500, l_grating=30, w_wg=0.5, w_etch=3 ):
    """ a is the length of the lattice \n
        D is the diameter of the hole \n
        d is the peorid of the gratings.
        """

    ld_fulletch = {"layer": 1, "datatype": 1}
    ld_grating = {"layer": 1, "datatype": 2}

    filename0 ="GC"
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
            x_start = l_taper_a + 6
        else:
            x_start += d_all[ii]
        
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
            points = [(0, w_wg/2), (l_taper_a, w_gc/2), (l_taper_a+l_grating, w_gc/2), (l_taper_a+l_grating, w_gc/2+w_etch), (l_taper_a, w_gc/2+w_etch), (0, w_wg/2+w_etch)]
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