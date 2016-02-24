#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, Gtk, GdkX11, GstVideo
from gi.repository import GdkPixbuf 

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
        button = Gtk.Button("Click")
        button.connect("clicked", self.on_click)
        hbox.pack_start(button, True, True, 0)
        window.show_all()
        
        
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("v4l2src", "webcam")
        mirror = Gst.ElementFactory.make("videoflip", "webcam-flip")
        mirror.set_property("method", "horizontal-flip")
        colorspace = Gst.ElementFactory.make("videoconvert")
        sink = Gst.ElementFactory.make("autovideosink", "app") # TODO check gtkglsink
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

    def on_click(self, button):
        print ("Hello")
        img = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 800, 600 )
        img.get_from_window(self.movie_window.window, self.movie_window.window.get_colormap(), 0, 0, 0, 0, 800, 600)
        buffer = self.player.emit('convert-sample', Gst.Caps.from_string('image/png'))
        with open('frame.png', 'w') as fh:
            fh.write(str(buffer))
        
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
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())

GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
