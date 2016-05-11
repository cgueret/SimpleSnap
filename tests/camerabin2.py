#!/usr/bin/env python
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init([])

camerabin = Gst.ElementFactory.make("camerabin")
webcam = Gst.ElementFactory.make('v4l2src')
webcam.set_property('device', '/dev/video1')
wrappercamerabinsrc = Gst.ElementFactory.make('wrappercamerabinsrc')
wrappercamerabinsrc.set_property('video-source', webcam)
camerabin.set_property('camera-source', wrappercamerabinsrc)
camerabin.set_state (Gst.State.PLAYING)
for c in ['viewfinder-supported-caps', 'image-capture-supported-caps']:
    print (c)
    for i in camerabin.get_property(c).to_string().split('; '):
        print (i)

print (camerabin.get_property('viewfinder-caps').to_string())
camerabin.set_state (Gst.State.NULL)

