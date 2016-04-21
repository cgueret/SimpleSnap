#!/usr/bin/env python
import gi
from simplesnap.camera import Camera
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GdkX11  # for window.get_xid() @UnusedImport
from gi.repository import GstVideo  # for sink.set_window_handle() @UnusedImport

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

def window_closed (widget, event, camera):
    widget.hide()
    camera.stop()
    Gtk.main_quit ()

class GTK_Main(object):
    def __init__(self):
        # Create the camera
        self.camera = Camera()
        
        # State variable for saving an image
        self.capturing = False
        
        # Prepare the main window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("SimpleSnap")
        window.set_default_size(500, 400)
        window.connect("destroy", self.on_quit)
        window.connect("delete-event", window_closed, self.camera)
        window.connect("key-release-event", self.on_key_released)
        vbox = Gtk.VBox()
        window.add(vbox)
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_double_buffered (True)
        vbox.pack_start(drawing_area, True, True, 0)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        button = Gtk.Button("Take photo")
        button.connect("clicked", self.on_take_photo)
        hbox.pack_start(button, True, True, 0)
        button = Gtk.Button("Quit")
        button.connect("clicked", self.on_quit)
        hbox.pack_start(button, True, True, 0)
        window.show_all()
        #window.fullscreen()
        window.realize()
        
        # Bind the view finder sink to the drawing area
        self.camera.bind_view_finder_to_widget(drawing_area)

        # Start the capture
        self.camera.start()        

    def on_take_photo(self, button):
        if self.capturing:
            return
        self.capturing = True        
        GLib.timeout_add_seconds(0, self.count_down, 3)
    
    def on_key_released(self, widget, event):
        if event.hardware_keycode == 123 and not self.capturing:
            self.capturing = True        
            GLib.timeout_add_seconds(0, self.count_down, 3)
        
    def count_down(self, value):
        # If there are more seconds, continue the count down     
        if value > 0:
            print (value)
            self.camera.show_count_down(value)
            GLib.timeout_add_seconds(1, self.count_down, value - 1)
        # If the count down is finished save the photo and pause
        elif value == 0:
            print ('Click !')
            self.camera.show_count_down('Click !')
            self.camera.take_photo()
            self.camera.pause()
            GLib.timeout_add_seconds(1, self.count_down, value - 1)
        # That's the post-pause count, resume the pipeline
        elif value < 0:
            self.capturing = False
            self.camera.hide_count_down()
            self.camera.start()
        
    def on_quit(self, button):
        print ("Bye !")
        self.camera.stop()
        Gtk.main_quit ()
        
if __name__ == "__main__":
    GObject.threads_init()
    Gtk.init([])
    Gst.init([])
    GTK_Main()
    Gtk.main()
