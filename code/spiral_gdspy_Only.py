import numpy 
import gdspy

# STEP 1: 
lib = gdspy.GdsLibrary(precision = 1e-10)

# create a new cell to save 
sp = lib.new_cell("spiral")
sp2 = lib.new_cell("spiral2")

# define the index of layer
ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 2, "datatype": 1}

def spiral(cell, w=0.5, pitch=2, r_min=10, r_max=40):
    """ 
    cell: is the reference of cell \n
    w is the width of waveguide \n
    pitch is the min distance between two waveguides. \n

    """
    path1 = gdspy.Path(w, (0, 0))
    path2 = gdspy.Path(w, (0, 0))
    path3 = gdspy.Path(w, (-r_min, 0))

    a = r_min
    k = r_max - r_min
    N = k/pitch
    

    def spiral1(u):
        theta = N * numpy.pi * u
        r = a + k*theta/( N * numpy.pi)
        x = r * numpy.cos(theta)
        y = r * numpy.sin(theta)
        return (x, y)

    def spiral2(u):
        theta = (N+1) * numpy.pi * u
        r = -( a + k*theta/( N * numpy.pi) )
        x = r * numpy.cos(theta)
        y = r * numpy.sin(theta)
        return (x, y)

    def dspiral_dt(u):
        theta = N * numpy.pi * u
        dx_dt = -numpy.sin(theta)
        dy_dt = numpy.cos(theta)
        # dx_dt = k*numpy.cos(theta) - (a + k*u)*N*numpy.pi*numpy.sin(theta)
        # dy_dt = k*numpy.sin(theta) + (a + k*u)*N*numpy.pi*numpy.cos(theta)
        return (dx_dt, dy_dt)
    
    def dspiral_dt2(u):
        theta = (N+1) * numpy.pi * u
        dx_dt = -numpy.sin(theta)
        dy_dt = numpy.cos(theta)
        # dx_dt = k*numpy.cos(theta) - (a + k*u)*N*numpy.pi*numpy.sin(theta)
        # dy_dt = k*numpy.sin(theta) + (a + k*u)*N*numpy.pi*numpy.cos(theta)
        return (dx_dt, dy_dt)

    # Add the parametric spiral to the path
    path1.parametric(spiral1, dspiral_dt)
    path2.parametric(spiral2, dspiral_dt2)
    path3.turn(r_min/2, 'rr')
    path3.turn(r_min/2, 'll')
    path3.rotate(numpy.pi/2, (-r_min, 0))

    cell.add(path1)
    cell.add(path2)
    cell.add(path3)

spiral(sp, w=0.45, r_max=100)

# lib.write_gds('./layout/spiral3.gds')
gdspy.LayoutViewer()