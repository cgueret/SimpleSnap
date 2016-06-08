#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from gi.repository import Gtk

from simplesnap.camera import Camera

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

def window_closed (widget, event, camera):
    widget.hide()
    camera.stop()
    Gtk.main_quit ()

class GTK_Main(object):
    def __init__(self):
        # Create the camera
        print ('Create camera')
        self.camera = Camera()
        
        # Prepare the main window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("SimpleSnap")
        window.set_default_size(500, 400)
        window.connect("destroy", self.on_quit)
        window.connect("delete-event", window_closed, self.camera)
        window.connect("key-release-event", self.on_key_released)
        
        
        # Make a first tab for the view finder
        vf_area = Gtk.DrawingArea()
        vf_area.set_double_buffered (True)
        
        #vbox = Gtk.VBox()
        #window.add(vbox)
        #vbox.pack_start(drawing_area, True, True, 0)
        #vbox.pack_start(hbox, False, False, 0)
        hbox = Gtk.HBox()
        button = Gtk.Button("Take photo")
        button.connect("clicked", self.on_take_photo)
        hbox.pack_start(button, True, True, 0)
        button = Gtk.Button("Quit")
        button.connect("clicked", self.on_quit)
        hbox.pack_start(button, True, True, 0)
        
        # Pack
        window.add(vf_area)
        
        # Show
        window.show_all()
        window.fullscreen()
        window.realize()
        
        # Bind the view finder sink to the drawing area
        self.camera.bind_view_finder_to_widget(vf_area)
        
        # Start the capture
        self.camera.start()        
        
    def on_take_photo(self, button):
        self.camera.take_photo()
    
    def on_key_released(self, widget, event):
        #print (event.hardware_keycode)
        if event.hardware_keycode == 123 or event.hardware_keycode == 36:
            self.camera.take_photo()
        else:
            self.on_quit(None)
        
    def on_quit(self, button):
        print ("Bye !")
        self.camera.stop()
        Gtk.main_quit ()
        
if __name__ == "__main__":
    Gtk.init([])
    Gst.init([])
    GTK_Main()
    Gtk.main()
