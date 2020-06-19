import numpy as np
import xlwt

a = [[0]*4]*29*2
b = a
pitch = a

f = xlwt.Workbook()
Sheet1 = f.add_sheet('Sheet1',cell_overwrite_ok=True)

pa_temp = [1, 2, 3, 4]
for pa_index in range(4):
    pa = np.loadtxt("./2D_parameters"+str(pa_temp[pa_index])+".txt")*1e6
    j = 1 # j is the index of row
    i = 0
    while i in range(len(pa)):
        Sheet1.write(j, 3*pa_index, pa[i])
        Sheet1.write(j, 3*pa_index + 1, pa[i+1])
        Sheet1.write(j, 3*pa_index + 2, pa[i] + pa[i + 1])
        i += 2
        j += 1
f.save('Conbination_parameters.xlsx')

