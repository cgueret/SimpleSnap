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
        #pipeline = "uvch264src device=/dev/video1 name=src "
        #pipeline += "src.imgsrc ! queue ! gdkpixbufsink sync=false "
        #pipeline += "src.vfsrc ! queue ! video/x-raw,format=(string)BGRA,width=320,height=240,framerate=20/1 ! gtksink name=gtk sync=false "
        pipeline = "v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! avdec_h264 ! tee name=t ! autovideoconvert ! queue ! gtksink name=gtk sync=false t. ! queue ! autovideoconvert ! videoscale ! capsfilter ! gdkpixbufsink name=buf sync=false"
        self.player = Gst.parse_launch(pipeline)
        print (self.player)
        
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

        self.player.set_state(Gst.State.PLAYING)        

    def on_click(self, button):
        print ("Click !")
        #camera = self.player.get_by_name('src')
        #print (camera.get_property('mode'))
        #print (camera.get_property('ready-for-capture'))
        #camera.emit('start-capture')
        #print (dir(camera))
        #i = camera.get_static_pad('imgsrc')
        #print (i)
        #q = Gst.ElementFactory.make("queue")
        #i.set_target(q)
        p = self.player.get_by_name('buf')
        buf = p.get_property('last-pixbuf')
        buf.savev('test.png', 'png', ['compression', 'tEXt::Title'], ['3', 'test'])
        
    def on_message(self, bus, message):
        if message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print ("Warning: %s" % err, debug)
        

GObject.threads_init()
Gtk.init([])
Gst.init([])
GTK_Main()
Gtk.main()
