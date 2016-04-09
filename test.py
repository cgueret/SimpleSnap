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
        webcam = Gst.ElementFactory.make("v4l2src", "webcam")
        
        wrapper = Gst.ElementFactory.make("wrappercamerabinsrc", "wrapper")
        wrapper.set_property('video-source', webcam)
        camerabin = Gst.ElementFactory.make("camerabin", "camerabin")
        camerabin.set_property('camera-source', wrapper)
        self.player = Gst.Pipeline.new("player")
        self.player.add(camerabin)
        self.player.set_state(Gst.State.PLAYING)        
        a = camerabin.get_property('image-capture-supported-caps').to_string().split(';')
        print (a)
        
        # Prepare the Gstreamer elements
        pipeline = "uvch264src device=/dev/video1 mode=1 name=src src.vfsrc "
        pipeline += "! video/x-raw,width=320,height=240,framerate=30/1 "
        pipeline += "! gtksink sync=false name=gtk"
        self.player = Gst.parse_launch(pipeline)
        
        # Prepare the main window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.add(self.player.get_by_name('gtk').get_property('widget'))
        vbox.pack_start(hbox, False, False, 0)
        button = Gtk.Button("Click")
        button.connect("clicked", self.on_click)
        hbox.pack_start(button, True, True, 0)
        window.show_all()
                
        # -> Listen to the bus
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.player.set_state(Gst.State.PLAYING)        

        camera = self.player.get_by_name('src')
        m = camera.get_property('mode')
        print (m)
        modes=type(m)
        still = modes(1)
        print (still)
        camera.set_property('mode', still)
        
    def on_click(self, button):
        print ("Click !")
        camera = self.player.get_by_name('src')
        m = camera.get_property('mode')
        modes=type(m)
        still = modes(1)
        camera.set_property('mode', still)
        #camera.set_property('mode', GstCameraBin2Mode.Image)
        print (camera.get_property('mode'))
        print (camera.get_property('ready-for-capture'))
        camera.emit('start-capture')
        
    def on_message(self, bus, message):
        if message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print ("Error: %s" % err, debug)

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        print (message_name)
        print (message.src)
        if message_name == "prepare-window-handle":
            print (dir(message.src))
            print (self.movie_window.window)
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.movie_window.window.xid)
        

GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
