#!/usr/bin/env python
import os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst
from gi.repository import GLib
from gi.repository import Gtk

def photo(binn):
    binn.set_property("location", "blah.jpg")
    binn.emit("start-capture")
    
def stop(binn):
    binn.set_state (Gst.State.NULL)
    Gtk.main_quit ()

def message(bus, message):
    if message.type != Gst.MessageType.STATE_CHANGED and message.type != Gst.MessageType.STREAM_STATUS:
        print ("{} {}".format(message.type, message.get_structure().get_name()))
    
Gst.init([])
Gtk.init([])

vf_caps = Gst.Caps.from_string('video/x-raw, width=1280, height=720, framerate=24/1')
#photo_caps = Gst.Caps.from_string('video/x-raw, width=1920, height=1080')
photo_caps = Gst.Caps.from_string('video/x-raw, width=2304, height=1536')

webcam = Gst.ElementFactory.make('v4l2src')
device = '/dev/video1' if os.path.exists('/dev/video1') else '/dev/video0'
webcam.set_property('device', device)
wrappercamerabinsrc = Gst.ElementFactory.make('wrappercamerabinsrc')
wrappercamerabinsrc.set_property('video-source', webcam)

vf_sink = Gst.ElementFactory.make('glimagesink')
vf_sink.set_property('sync', False)

camerabin = Gst.ElementFactory.make("camerabin")
camerabin.set_property('mute', True)
camerabin.set_property('camera-source', wrappercamerabinsrc)
camerabin.set_property('viewfinder-sink', vf_sink)
camerabin.set_property('viewfinder-caps', vf_caps)
camerabin.set_property('image-capture-caps', photo_caps)

bus = camerabin.get_bus()
bus.add_signal_watch()
bus.connect("message", message)
        
camerabin.set_state (Gst.State.PLAYING)

GLib.timeout_add_seconds(2, photo, camerabin)
GLib.timeout_add_seconds(6, stop, camerabin)

Gtk.main()

