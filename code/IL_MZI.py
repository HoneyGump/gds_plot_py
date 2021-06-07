from shapely.geometry import Polygon, Point

from gdshelpers.geometry.chip import Cell
from gdshelpers.geometry import geometric_union
# from gdshelpers.geometry import convert_to_layout_objs

from gdshelpers.helpers import positive_resist

from gdshelpers.parts.port import Port
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.splitter import MMI

import numpy as np
import gdspy


def IL_mmi(origin=(0,0), len_in=500, radius=10, num_roundtrip=3, len_deltaL=250, w_etch=3):
        """
        total delta L =  4*len_delta_L * num_rountrip
        """
        # coupler_params = {
        # 'width': 0.45,
        # 'full_opening_angle': np.deg2rad(40),
        # 'grating_period': 0.64,
        # 'grating_ff': 0.546875,
        # 'n_gratings': 20,
        # 'taper_length': 16,
        # }
        mmi_params ={
                'length': 31.37,
                'width': 6,
                'taper_width':2.9,
                'taper_length':20,
        }
        # gc_start
        # gc_start = GratingCoupler.make_traditional_coupler(origin, angle=-np.pi, **coupler_params)
        # staright wg
        wg_start = Waveguide(origin,angle=0, width=0.5)
        wg_start.add_straight_segment(10)
        # mmi_in
        mmi_in = MMI.make_at_port(wg_start.port, num_inputs=1, num_outputs=2, **mmi_params)
        # mmi_in.
        # len_in is the length of the input straight wg
        # len_out is the length of the out straight wg
        #
        # len_in = 500
        len_out = len_in
        # len_deltaL = 400
        # radius = 10
        gap = 10
        # num_roundtrip = 3
        # port 1
        wg1 = Waveguide.make_at_port(mmi_in.left_branch_port)
        wg1.add_straight_segment(len_in)
        i=0
        while i < num_roundtrip:
                wg1.add_bend(np.pi, radius)
                wg1.add_straight_segment(len_deltaL)
                wg1.add_bend(-np.pi, radius)
                wg1.add_straight_segment(len_deltaL)
                i += 1
        wg1.add_straight_segment(6*radius + 3*gap)
        i=0
        while i < num_roundtrip:
                wg1.add_straight_segment(len_deltaL)
                wg1.add_bend(-np.pi, radius)
                wg1.add_straight_segment(len_deltaL)
                wg1.add_bend(np.pi, radius)
                i += 1
        wg1.add_straight_segment(len_out)
        # port 2
        wg2 = Waveguide.make_at_port(mmi_in.right_branch_port)
        wg2.add_straight_segment(len_in + 2*radius+gap)
        i=0
        while i < num_roundtrip:
                wg2.add_bend(np.pi, radius)
                wg2.add_bend(-np.pi, radius)
                i += 1
        wg2.add_straight_segment(2*radius + gap)
        i=0
        while i < num_roundtrip:
                wg2.add_bend(-np.pi, radius)
                wg2.add_bend(np.pi, radius)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                i += 1
        wg2.add_straight_segment(len_out + 2*radius+gap)
        # mmi_out
        mmi_out = MMI.make_at_port(wg1.port, num_inputs=2, num_outputs=1, **mmi_params)
        # straight wg
        wg_end = Waveguide.make_at_port(mmi_out.right_branch_port)
        wg_end.add_straight_segment(10)
        
        # convert to positive resist
        layout = positive_resist.convert_to_positive_resist([ mmi_in, mmi_out, wg1, wg2, wg_end, wg_start], w_etch, outer_resolution=1e-3)

        gap = 10
        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon1 = Polygon(outer_corners)
        origin = wg_end._current_port.origin
        print("End Point： ",  origin)
        origin[0] = origin[0]  + 2*gap
        outer_corners = [origin, (origin[0], origin[1]+2*gap), (origin[0]-2*gap, origin[1]+2*gap), (origin[0]-2*gap, origin[1]-2*gap), (origin[0], origin[1]-2*gap)]
        polygon2 = Polygon(outer_corners)
        polygon = polygon1.union(polygon2)

        layout_fixed = layout.difference(polygon)

        return layout_fixed

layout = IL_mmi((0,0), num_roundtrip=1, len_deltaL=500)

layout2 = IL_mmi((0,-150), num_roundtrip=2, len_deltaL=500)

cell = Cell('MZI_')

cell.add_to_layer(1, layout)
cell.add_to_layer(1, layout2)

cell.save('./layout/IL_MZI.gds')
# cell.show()
