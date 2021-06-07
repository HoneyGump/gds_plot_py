#%%
import numpy as np
import gdspy
import scipy.io as scio


lib = gdspy.GdsLibrary( precision=1e-10)

# Geometry must be placed in cells.
devices = lib.new_cell("devices")
device1 = lib.new_cell("device1")
device2 = lib.new_cell("device2")



ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 1}

pa = np.loadtxt('./dat_apozied/2D_parameters2.txt')*1e6
#%%
x0 = -6
wg_length = 12.6

xp = wg_length
x_begin = xp
w_wg = 0.5
w_etch = 3
w = 10
l_grating = 500

#%% 
wg = lib.new_cell('waveguides')
l_wg = 400
points = [(0, w_wg/2), (-l_wg, w_wg/2), (-l_wg, w_wg/2+w_etch), (0, w_wg/2+w_etch)]
poly = gdspy.Polygon(points, **ld_fulletch)
wg.add(poly)
points = [(0, -w_wg/2), (-l_wg, -w_wg/2), (-l_wg, -w_wg/2-w_etch), (0, -w_wg/2-w_etch)]
poly = gdspy.Polygon(points, **ld_fulletch)
wg.add(poly)

xp_temp = [10, 12.6, 15]
pa_temp = [1, 2, 3, 4]
y_pos_step = -100
y_pos = 0


for pa_index in range(4):
    pa = np.loadtxt("./dat_apozied/2D_parameters"+str(pa_temp[pa_index])+".txt")*1e6
    
    for y_pos_index in range(3):
        xp2 = 0
        xp = xp_temp[y_pos_index]
        grating = lib.new_cell("FocusGrating_"+ "pa" + str(pa_temp[pa_index]) + "_lwg" + str(xp) )
        lineGrating = lib.new_cell("LineGrating_"+ "pa" + str(pa_temp[pa_index]) + "_lwg" + str(xp))
        GC_theta = 23/180*np.pi
        GC_theta2 = 20/180*np.pi
        #%% 
        i=0
        while i<len(pa):
            a =  float(pa[i])
            b =  float(pa[i+1])
            arc = gdspy.Round(
                (0, 0),
                xp+a,
                inner_radius=xp,
                initial_angle= -GC_theta,
                final_angle= GC_theta,
                number_of_points=128,
                **ld_grating
            )
            grating.add(arc)

            points = [(xp2, -w/2), (xp2, w/2), (xp2+a, w/2), (xp2+a, -w/2)]
            poly = gdspy.Polygon(points, **ld_fulletch) 
            lineGrating.add(poly)

            pitch = a + b   
            xp += pitch
            xp2 += pitch
            i += 2

        GC_theta = GC_theta2
        points = [(0, w_wg/2), (xp*np.cos(GC_theta), xp*np.sin(GC_theta)), (xp*np.cos(GC_theta), xp*np.sin(GC_theta) + w_etch), (0, w_wg/2 + w_etch)]
        poly = gdspy.Polygon(points, **ld_fulletch)
        grating.add(poly)

        poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
        grating.add(poly)

        xp2 += 6
        points = [(x0 - l_grating, w_wg/2), (x0, w/2), (xp2, w/2), (xp2, w/2+w_etch), (x0, w/2+w_etch), (x0 - l_grating, w_wg/2+w_etch)]
        poly = gdspy.Polygon(points, **ld_fulletch)
        lineGrating.add(poly)

        poly = gdspy.Polygon(points, **ld_fulletch).mirror((0,0), (1,0))
        lineGrating.add(poly)

        ref_wg = gdspy.CellReference(wg, (0, y_pos*y_pos_step + pa_index*y_pos_step))
        device1.add(ref_wg)

        ref_gc = gdspy.CellReference(grating, (0, y_pos*y_pos_step + pa_index*y_pos_step))
        device1.add(ref_gc)

        ref_gc = gdspy.CellReference(grating, (-l_wg, y_pos*y_pos_step + pa_index*y_pos_step), rotation=180)
        device1.add(ref_gc)

        ref_wg = gdspy.CellReference(wg, (1500 + (x0-l_grating) , y_pos*y_pos_step + pa_index*y_pos_step))
        device2.add(ref_wg)

        ref_gc = gdspy.CellReference(lineGrating, (1500, y_pos*y_pos_step + pa_index*y_pos_step))
        device2.add(ref_gc)

        ref_gc = gdspy.CellReference(lineGrating, (1500 + 2*(x0-l_grating)-l_wg, y_pos*y_pos_step + pa_index*y_pos_step), rotation=180)
        device2.add(ref_gc)

        y_pos += 1

ref1 = gdspy.CellReference(device1)
ref2 = gdspy.CellReference(device2)
devices.add([ref1, ref2])

ld_fulletch = {"layer": 1, "datatype": 1}

x0 = -200
y0 = 50
x_step = -500
y_step = -400
num = '21'
letter = 'ABCD'
print(len(letter))
print(len(num))
for i in range(len(letter)):
    for j in range(len(num)):
        text = letter[i] + num[j]
        com = lib.new_cell(text)
        com.add(gdspy.Text(text, 40, (x0 + j*x_step, y0 + i*y_step), **ld_fulletch))
        ref = gdspy.CellReference(com)
        devices.add(ref)

x0 = 700
y0 = 50
x_step = -500
y_step = -400
num = '3'
letter = 'ABCD'
print(len(letter))
print(len(num))
for i in range(len(letter)):
    for j in range(len(num)):
        text = letter[i] + num[j]
        com = lib.new_cell(text)
        com.add(gdspy.Text(text, 40, (x0 + j*x_step, y0 + i*y_step), **ld_fulletch))
        ref = gdspy.CellReference(com)
        devices.add(ref)

lib.write_gds('test.gds')
gdspy.LayoutViewer()

