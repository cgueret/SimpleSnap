#!/usr/bin/env python
import os
import gi
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
from datetime import datetime

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

def window_closed (widget, event, pipeline):
    widget.hide()
    pipeline.set_state(Gst.State.NULL)
    Gtk.main_quit ()

class GTK_Main(object):
    def __init__(self):
        # Define the pipeline
        pipeline_rpi = "v4l2src device=/dev/video0 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! omxh264dec ! tee name=t ! queue ! autovideoconvert ! videoscale ! video/x-raw,width=320,height=240 ! textoverlay name=timer ! ximagesink name=viewfinder sync=false t.  ! queue ! autovideoconvert ! gdkpixbufsink name=buf sync=false"
        pipeline_laptop = "v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! avdec_h264 ! tee name=t ! queue ! autovideoconvert ! videoscale ! video/x-raw,width=768,height=576 ! textoverlay name=timer ! glimagesink name=viewfinder sync=false t. ! queue ! autovideoconvert ! gdkpixbufsink name=buf sync=false"
        pipeline = pipeline_laptop if os.path.exists('/dev/video1') else pipeline_rpi
        self.player = Gst.parse_launch(pipeline)
        
        # Prepare the main window
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("SimpleSnap")
        window.set_default_size(500, 400)
        window.connect("destroy", window_closed, self.player)
        window.connect("delete-event", window_closed, self.player)
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
        
        # Adjust size and position of the count down
        p = self.player.get_by_name('timer')
        p.set_property('font-desc', 'Ubuntu,Bold 70')
        p.set_property('draw-shadow', False)
        p.set_property('draw-outline', False)
        #p.set_property('text', '3 2 1 0')
        
        # Bind the view finder sink to the drawing area
        xid = drawing_area.get_window().get_xid()
        view_finder = self.player.get_by_name('viewfinder')
        view_finder.set_window_handle (xid)
        
        # -> Listen to the bus
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)

        self.player.set_state(Gst.State.PLAYING)        

    def on_take_photo(self, button):
        GLib.timeout_add_seconds(0, self.count_down, 3)
    
    def count_down(self, value):
        print (value)
        p = self.player.get_by_name('timer')

        # If there are more seconds, continue the count down     
        if value > 0:
            p.set_property('text', value)
            GLib.timeout_add_seconds(1, self.count_down, value - 1)
        # If the count down is finished save the photo and pause
        elif value == 0:
            p.set_property('text', '')
            print ('Click !')
            self._save_photo()
            self.player.set_state(Gst.State.PAUSED)
            GLib.timeout_add_seconds(1, self.count_down, value - 1)
        # That's the post-pause count, resume the pipeline
        elif value < 0:
            self.player.set_state(Gst.State.PLAYING)
        
    def on_quit(self, button):
        print ("Bye !")
        self.player.set_state(Gst.State.NULL)
        Gtk.main_quit ()
        
    def on_message(self, bus, message):
        if message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print ("Warning: %s" % err, debug)
        
    def _save_photo(self):
        os.makedirs('./photos', exist_ok=True)
        
        d = datetime.now()
        file_name = "./photos/{}.jpg".format(d.isoformat(' ').split('.')[0])
        
        params_png = {'compression': '3',
                      'tEXt::Title': d.isoformat(' ').split('.')[0]
                  }
        params_jpg = {'quality': '95'}
        params = params_jpg
        
        p = self.player.get_by_name('buf')
        buf = p.get_property('last-pixbuf')
        buf.savev(file_name, 'jpeg', list(params.keys()), list(params.values()))

if __name__ == "__main__":
    GObject.threads_init()
    Gtk.init([])
    Gst.init([])
    GTK_Main()
    Gtk.main()
