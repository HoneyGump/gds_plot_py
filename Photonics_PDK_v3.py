import numpy as np
import gdspy

ld_fulletch = {"layer": 1, "datatype": 1}
ld_grating = {"layer": 1, "datatype": 3}

gdspy.Polygon()
class Part:
    def __init__(self):
        self.layer = 1
        self.datatype = 1
        self.width = 0.45
        self.port = []

if __name__=='__main__':
    p = Part()
    p.datatype = 3
    p.port=[3,4]