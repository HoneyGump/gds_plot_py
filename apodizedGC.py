import numpy as np
import gdspy
import scipy.io as scio

# Load some data about period 
# we get the diameter of hole: D
# we get the peorid: d_goal
dir_file = './data_apodized/Peorid_Diameter_min80_all_SiO2.mat'
temp = scio.loadmat(dir_file)

# STEP 1:
# definition of some basic parameters 
# D is the diameter of hole
# d is the pitch in the x direction or period dierection
# usually, we set d = a*3
a = 0.23   # a is the distance bwt two holes
pitch_y = a*np.sqrt(3) # pitch in the y direction
period_num = 29
w = 10 # width of grating
w_wg = 0.5 # width of waveguides
w_etch = 3 # width of etch
l_taper_a = 500 # length of grating start taper for output
l_taper_b = 100 # length of grating end taper for output
l_wg = 200 # length of waveguides
l_grating = 25 # the length of grating
x0 = -6 # the start position of grating, this is a flat region

# STEP 2: 
# creat the gdslibrary
lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
device = lib.new_cell('device2')

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 2}

# create the cell: waveguides
wg = lib.new_cell('waveguides')
points = [(0, w_wg/2), (-l_wg, w_wg/2), (-l_wg, w_wg/2+w_etch), (0, w_wg/2+w_etch)]
poly = gdspy.Polygon(points, **ld_fulletch)
wg.add(poly)
poly = gdspy.Polygon(points, **ld_fulletch).mirror((0, 0), (1, 0))
wg.add(poly)

# if D > 0.18 , D = 0.18
D = temp['D']*1e6
D2 = np.empty(shape = [29,1])
for D_index in range(D.shape[0]):
    D2[D_index,0] = D[D_index,0]
    if D[D_index,0] >= 0.180:
        D2[D_index,0] = 0.180

filename0 ="GC"
num_GC = 0
num_block = 0
for index_D in range(2):
    if index_D == 1:
        D = D2
    for index_d_comp in range(5):
        # create the main body of phtonic crystal grating coupler
        d_goal = temp['d_goal']*1e6 - index_d_comp * 0.005
        filename = filename0 + "_a"+str(int(a*1e3)) + "_" + str(int(index_D)) + "_" + str(int(index_d_comp)) 
        grating = lib.new_cell(filename)
        for ii in range(period_num):
            # this is for a variable period
            if ii == 0:
                x_start = 0
            else:
                x_start += d_goal[(ii,0)]
            
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
        points = [(x0-l_taper_a, w_wg/2), (x0, w/2), (l_grating, w/2), (l_grating + l_taper_b,0), (l_grating + l_taper_b+w_etch, 0), (l_grating, w/2+w_etch), (x0, w/2+w_etch), (x0-l_taper_a, w_wg/2+w_etch)]
        poly = gdspy.Polygon(points, **ld_fulletch)
        grating.add(poly)

        poly = gdspy.Polygon(points, **ld_fulletch).mirror((0, 0), (1, 0))
        grating.add(poly)
        
        # Assembled into a grating pair: 2 grating coupler and straight waveguide
        y_position = 100*num_GC + 100*num_block
        ref = gdspy.CellReference(grating, (0, y_position))
        ref2 = gdspy.CellReference(wg, (-l_taper_a + x0, y_position))
        ref3 = gdspy.CellReference(grating, ((-l_taper_a + x0)*2-l_wg, y_position), rotation=180)
        device.add([ref, ref2, ref3])
        num_GC = num_GC - 1 # decide the direction of device, usually negative means in -y direction

    # one block is sweep one parameter
    num_block = num_block - 1

# STEP 3 save as gds format
# get an array instance of device
devices = lib.new_cell("Devices2")
devices.add(gdspy.CellArray(device, 4, 1, (1500,0)))

# Save the library in a file called 'first.gds'.
lib.write_gds('ApodizedGC.gds')
gdspy.LayoutViewer()

