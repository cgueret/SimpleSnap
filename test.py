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
        #window.set_resizable(False)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        gtksink = Gst.ElementFactory.make("gtksink", "app") # TODO check gtkglsink
        gtksink.set_property("sync", False)
        vbox.add(gtksink.get_property('widget'))
        vbox.pack_start(hbox, False, False, 0)
        button = Gtk.Button("Click")
        button.connect("clicked", self.on_click)
        hbox.pack_start(button, True, True, 0)
        window.show_all()
        
        # Prepare the pipeline        
        self.player = Gst.Pipeline.new("player")
        
        # Add the webcam as a source
        source = Gst.ElementFactory.make("v4l2src", "webcam")
        self.player.add(source)
        
        # Mirror the image
        mirror = Gst.ElementFactory.make("videoflip", "webcam-flip")
        mirror.set_property("method", "horizontal-flip")
        self.player.add(mirror)
        source.link(mirror)
        
        # Add a colorspace
        colorspace = Gst.ElementFactory.make("videoconvert")
        self.player.add(colorspace)
        mirror.link(colorspace)
        
        # Split the channel
        tee = Gst.ElementFactory.make("tee")
        self.player.add(tee)

        # Add the gtksink on one branch    
        gtkqueue = Gst.ElementFactory.make("queue", "gtkqueue")
        gtkqueue.link(gtksink)
        self.player.add(gtkqueue)
        gtkpad = tee.get_request_pad('src_%u')
        print ("Obtained request pad {} for gtk".format( gtkpad.get_name()))
        a = gtkpad.link(gtkqueue.get_static_pad('sink'))
        print (a)
        
        # and the gdkpixbuf on the other
        pixbufqueue = Gst.ElementFactory.make("queue")
        self.player.add(pixbufqueue)
        pixbuf = Gst.ElementFactory.make("gdkpixbufsink")
        self.player.add(pixbuf)
        pixbufqueue.link(pixbuf)
        pixbufpad = tee.get_request_pad('src_%u')
        print ("Obtained request pad {} for pixbuf".format( pixbufpad.get_name()))
        a = pixbufpad.link(pixbufqueue.get_static_pad('sink'))
        print (a)
        
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        self.player.set_state(Gst.State.PLAYING)        

    def on_click(self, button):
        print ("Hello")
        #self.sink.save('a.jpg','jpeg', {'quality': '100'})
        buffer = self.player.emit('convert-sample', Gst.Caps.from_string('image/png'))
        with open('frame.png', 'w') as fh:
            fh.write(str(buffer))
        

GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
