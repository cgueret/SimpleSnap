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
        # Prepare the Gstreamer elements

        # -> The sink to show the current image
        gtksink = Gst.ElementFactory.make("gtksink", "view") # TODO check gtkglsink
        gtksink.set_property("sync", False)
        
        # -> Camerabin
        source = Gst.ElementFactory.make("camerabin", "webcam")
        source.set_property('viewfinder-sink', gtksink)
        source.set_property('mute', True)
        
        # -> prepare the pipeline        
        self.player = Gst.Pipeline.new("player")
        self.player.add(source)
        
        # -> Listen to the bus
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        # Prepare the main window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.add(gtksink.get_property('widget'))
        vbox.pack_start(hbox, False, False, 0)
        button = Gtk.Button("Click")
        button.connect("clicked", self.on_click)
        hbox.pack_start(button, True, True, 0)
        window.show_all()
                
        self.player.set_state(Gst.State.PLAYING)        

    def on_click(self, button):
        print ("Hello")
        camera = self.player.get_by_name('webcam')
        camera.emit('start-capture')
        a = camera.get_property('image-capture-caps')
        print (a.to_string())
        caps =  Gst.Caps.from_string('image/png,width=1920,height=1080')
        

GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
