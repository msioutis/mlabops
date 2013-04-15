#!/usr/bin/python

import pprint
from planetlab.types import *

# name  : the slice name
# index : the index into the iplist for each node to assign to this slice
# attr  : a list of slice attributes.
slice_list = [

    Slice(name='gt_partha',              index=0, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name='iupui_ndt',              index=1, attrs=[
                    Attr('MeasurementLab',    capabilities='VXC_PROC_WRITE'),
                    Attr('MeasurementLab',    disk_max='60000000'),
                    Attr('MeasurementLabK32', disk_max='60000000'), ],
                    ipv6=['mlab4.nuq01', 'mlab4.nuq02']),

    Slice(name='iupui_npad',             index=2, attrs=[
                    Attr(None,                initscript='iupui_npad_initscript'),
                    Attr('MeasurementLab',    capabilities='VXC_PROC_WRITE'),
                    Attr('MeasurementLab',    disk_max='10000000'),
                    Attr('MeasurementLabK32', disk_max='10000000'),
                    Attr('MeasurementLabK32', vsys='web100_proc_write'),
                    Attr('MeasurementLabK32', pldistro='mlab'), ],
                    ipv6="all"),

    Slice(name='mpisws_broadband',       index=3, attrs=[
                    Attr(None,                initscript='mpisws_broadband_initscript'),
                    Attr('MeasurementLab',    capabilities='CAP_NET_RAW'),
                    Attr('MeasurementLab',    disk_max='35000000'),
                    Attr('MeasurementLabK32', capabilities='CAP_NET_RAW'),
                    Attr('MeasurementLabK32', disk_max='35000000'), ],
                    ipv6=['mlab4.nuq01', 'mlab4.nuq02']),

    Slice(name="northwestern_windrider", index=4, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name="uw_geoloc4",             index=5, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name="samknows_ispmon",        index=7, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name="gt_bismark",             index=8, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name="mlab_neubot",            index=9, ipv6=['mlab4.nuq01', 'mlab1.trn01', 'mlab4.nuq02']),
    Slice(name="michigan_1",             index=10, ipv6=['mlab4.nuq01', 'mlab4.nuq02']),
    Slice(name='princeton_namecast',     index=11, attrs=[
                    Attr('MeasurementLab',    capabilities='CAP_NET_BIND_SERVICE'),
                    Attr('MeasurementLabK32', capabilities='CAP_NET_BIND_SERVICE'), ],
                    ipv6=['mlab4.nuq01', 'mlab4.nuq02']),

    Slice(name="pl_netflow"),
    Slice(name="pl_default"),
    Slice(name="princeton_comon"),
    Slice(name="princeton_slicestat"),
    Slice(name="mlab_ops", attrs=[
                    Attr(None, vsys='slice_restart'),
                    Attr(None, vsys='slice_recreate'),
               ]),
]

