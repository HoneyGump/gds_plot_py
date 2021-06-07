import numpy as np
import gdspy

def line_focusing(u):
    global q
    lambda0 = 1.55
    n_eff = 2.828
    # q = 1
    n_c = 1.44
    theta_c = 8/180*np.pi
    theta0_rad = 20/180*np.pi
    phi = -theta0_rad/2*(2*u-1)
    r = q*lambda0/(n_eff - n_c*np.sin(theta_c)*np.cos(phi))
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return (x, y)

def get_Point_z(n_eff, n_cladding, theta_c, lambda0, q):
    """ theta_c unit is rad"""
    z = q*lambda0/(n_eff - n_cladding*np.cos(theta_c))
    return z

def line_focusing_q(q):
    line_focusing(u)


lambda0 = 1.55
n_eff = 2.828
q = 20
n_cladding = 1.44
theta_c = 8/180*np.pi

z = get_Point_z(n_eff, n_cladding, theta_c, lambda0, q)
print(z)
# # STEP 1: 
# lib = gdspy.GdsLibrary(precision = 1e-10)

# # create a new cell to save 
# gc = lib.new_cell("GC")
# ground = lib.new_cell("ground")
# tooth = lib.new_cell("tooth")

# # define the index of layer
# ld_fulletch = {"layer": 1, "datatype": 1}
# ld_grating = {"layer": 2, "datatype": 1}

# path_line = gdspy.Path(0.3, (0,0))
# path_line.parametric(line_focusing, tolerance=0.001)

# gc.add(path_line)


# lib.write_gds('test2.gds')
# gdspy.LayoutViewer()