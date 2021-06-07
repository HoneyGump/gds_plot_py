import Photonics_PDK as pdk
import gdspy


lib = gdspy.GdsLibrary( precision=1e-10)
maek = pdk.Mark_crossmark(lib)
lib.write_gds('test_mark.gds')

# import numpy as np