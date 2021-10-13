# create ring 
ring = lib.new_cell('ring_R'+str(int(radius_ring))+'_gap'+str(int(gap*1000)))
points = [(0, -w_wg/2), (l_wg, -w_wg/2), (l_wg, w_wg/2), (0, w_wg/2)]
poly = gdspy.Polygon(points)
arc = gdspy.Round(
    (l_wg/2, -gap-w_wg-radius_ring),
    radius_ring+w_wg/2,
    inner_radius=radius_ring-w_wg/2 ,
    tolerance=0.001,
)
Photonics_PDK.convert_to_positive_resist(ring, [poly, arc], buffer_radius=3)