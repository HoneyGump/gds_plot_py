from scipy import integrate
import gdspy
import numpy as np

R0 = 5 # unit is um
b = 2.49

def fun_1(theta):
    return (np.cos(theta))**((b-1)/b)

def fun_2(theta):
    return np.sin(theta) * (np.cos(theta))**(-1/b)

F1 = integrate.quad(fun_1, np.pi/4, np.pi/2)[0]
F2 = integrate.quad(fun_2, np.pi/4, np.pi/2)[0]

x0 = R0 * F2 / (F1 + F2)
A = (F1 + F2) / R0

print("x0: ", x0)
print("A: ", A)

def curve_opt1(t):
    t = t*np.pi/4 + np.pi/4
    x = x0 + 1/A*integrate.quad(fun_1, np.pi/4, t)[0]
    y = R0 - x0 + 1/A*integrate.quad(fun_2, np.pi/4, t)[0]
    return (x, y)

def curve_opt2(t):
    (x1, y1) = curve_opt1(t)
    x = R0 - y1
    y = R0 - x1
    return (x, y)


w_wg = 0.45
curve1 = gdspy.Path(w_wg, (0,0))
curve1.parametric(curve_opt1)

curve2 = gdspy.Path(w_wg, (0,0))
curve2.parametric(curve_opt2)

curve3 = gdspy.Path(w_wg, (0,0))
curve3.turn(R0,'l', layer=1)

lib = gdspy.GdsLibrary()
cell = lib.new_cell("cell")
cell.add(curve1)
cell.add(curve2)
cell.add(curve3)

gdspy.LayoutViewer()