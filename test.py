#!/usr/bin/env python
import sys, os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, Gtk
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

class GTK_Main(object):
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        vbox.pack_start(hbox, False, False, 0)
        self.button = Gtk.Button("Click")
        hbox.pack_start(self.button, True, True, 0)
        window.show_all()
        
        
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("v4l2src", "webcam")
        mirror = Gst.ElementFactory.make("videoflip", "webcam-flip")
        mirror.set_property("method", "horizontal-flip")
        colorspace = Gst.ElementFactory.make("videoconvert")
        sink = Gst.ElementFactory.make("autovideosink", "app")
        sink.set_property("sync", False)
        
        self.player.add(source)
        self.player.add(mirror)
        self.player.add(colorspace)
        self.player.add(sink)
        source.link(mirror)
        mirror.link(colorspace)
        colorspace.link(sink)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.player.set_state(Gst.State.PLAYING)        

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.button.set_label("Start")
        
    def on_sync_message(self, bus, message):
        print ("hello")
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())

GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
