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
        print ('create camera')
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
        
        
        # Prepare the notebook
        notebook = Gtk.Notebook()
        
        # Make a first tab for the view finder
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_double_buffered (True)
        notebook.append_page(drawing_area, Gtk.Label("live"))
        
        # Make a second one to show the last image
        frame = Gtk.AspectFrame()
        last_photo = Gtk.Image()
        frame.add(last_photo)
        #notebook.append_page(frame, Gtk.Label("last photo"))
        
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
        window.add(notebook)
        
        # Show
        window.show_all()
        #window.fullscreen()
        window.realize()
        
        # Bind the view finder sink to the drawing area and the window to
        # show the last photo to the GtkImage
        self.camera.bind_last_photo_to_image(last_photo)
        self.camera.bind_view_finder_to_widget(drawing_area)

        # Start the capture
        self.camera.start()        

        last_photo.set_from_file('./photos/2016-05-11 22:56:06.jpg')
        
    def on_take_photo(self, button):
        self.camera.take_photo()
    
    def on_key_released(self, widget, event):
        print (event.hardware_keycode)
        if event.hardware_keycode == 123:
            self.camera.take_photo()
        if event.hardware_keycode == 36:
            print ('exit')
        
    def on_quit(self, button):
        print ("Bye !")
        self.camera.stop()
        Gtk.main_quit ()
        
if __name__ == "__main__":
    Gtk.init([])
    Gst.init([])
    GTK_Main()
    Gtk.main()
