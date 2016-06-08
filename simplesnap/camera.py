'''
Created on 11 May 2016

@author: cgueret
'''
import os
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst
from gi.repository import GLib
from gi.repository import GdkX11  # for window.get_xid() @UnusedImport
from gi.repository import GstVideo  # for sink.set_window_handle() @UnusedImport
from gi.repository import GstPbutils
from datetime import datetime

class Camera(object):
    def __init__(self):
        '''
        Constructor
        '''
        self.capturing = False
        
        # Set the video and photo caps
        VF_CAPS = Gst.Caps.from_string('video/x-raw, width=1280, height=720, framerate=30/1')
        #VF_CAPS = Gst.Caps.from_string('video/x-raw, width=800, height=600, framerate=30/1')
        #photo_caps = Gst.Caps.from_string('video/x-raw, width=1920, height=1080')
        PHOTO_CAPS = Gst.Caps.from_string('video/x-raw, width=2304, height=1536')

        PROFILE = GstPbutils.EncodingVideoProfile.new(Gst.Caps("image/jpeg"), 
                                                      None, None, 1)
        
        # Create an instance of the webcam
        print ('Create webcam')
        webcam = Gst.ElementFactory.make('v4l2src')
        webcam.set_property('device', '/dev/video1')
        wrappercamerabinsrc = Gst.ElementFactory.make('wrappercamerabinsrc')
        wrappercamerabinsrc.set_property('video-source', webcam)

        # Create a view finder        
        print ('Create vf sink')
        self._vfsink = Gst.ElementFactory.make('glimagesink')
        self._vfsink.set_property('sync', False)
        
        # Filter to swap the video and add an overlay
        vf_filter = Gst.ElementFactory.make('bin')
        vf_flip = Gst.ElementFactory.make('videoflip')
        vf_flip.set_property("method", "horizontal-flip")
        vf_overlay = Gst.ElementFactory.make('textoverlay', 'timer')
        vf_overlay.set_property('font-desc', 'Ubuntu,Bold 70')
        vf_filter.add(vf_flip)
        vf_filter.add(vf_overlay)
        vf_flip.link(vf_overlay)
        
        # Create the camera bin
        print ('Create camera bin')
        self._camerabin = Gst.ElementFactory.make("camerabin")
        self._camerabin.set_property('mute', True)
        self._camerabin.set_property('camera-source', wrappercamerabinsrc)
        self._camerabin.set_property('viewfinder-sink', self._vfsink)
        self._camerabin.set_property('viewfinder-filter', vf_overlay)
        self._camerabin.set_property('viewfinder-caps', VF_CAPS)
        self._camerabin.set_property('image-capture-caps', PHOTO_CAPS)
        #self._camerabin.set_property('image-profile', PROFILE)
        
        # Create bus to get events from GStreamer pipeline
        bus = self._camerabin.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_message)
    
    def get_widget(self):
        '''
        Return the Gtk widget for the viewfinder
        '''
        return self._vfsink.get_property('widget')
    
    def bind_view_finder_to_widget(self, widget):
        '''
        Connect the view finder to a Widget
        '''
        xid = widget.get_window().get_xid()
        self._vfsink.set_window_handle(xid)
            
    def _on_message(self, bus, message):
        '''
        Print a message received from Gstreamer
        '''
        if message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print ('Warning: %s' % err, debug)
        elif message.type == Gst.MessageType.ELEMENT:
            if message.has_name("image-done"):
                self.capturing = False
                self._set_count_down('')
                filename = message.get_structure().get_string("filename")
                print (filename)
            
    def take_photo(self):
        if self.capturing:
            return
        self.capturing = True        
        GLib.timeout_add_seconds(0, self._count_down, 3)

    def _count_down(self, value):
        # If there are more seconds, continue the count down     
        if value > 0:
            print (value)
            self._set_count_down(value)
            GLib.timeout_add_seconds(1, self._count_down, value - 1)
        # If the count down is finished save the photo and pause
        elif value == 0:
            print ('Click !')
            self._set_count_down('Click !')
            GLib.timeout_add(500, self._save_photo)
        
    def _save_photo(self):
        '''
        Take a photo
        '''
        os.makedirs('./photos', exist_ok=True)
        
        # Get a timestamp
        d = datetime.now()
        timestamp = d.isoformat(' ').split('.')[0]
        
        # Set the file name
        file_name = './photos/{}.jpg'.format(timestamp)
        self._camerabin.set_property("location", file_name)
        
        # Emit the request
        self._camerabin.emit("start-capture")

        
    def _set_count_down(self, value):
        '''
        Show a particular count down value
        '''
        overlay = self._camerabin.get_by_name('timer')
        overlay.set_property('text', value)
        
    def start(self):
        '''
        Start the pipeline
        '''
        self._camerabin.set_state(Gst.State.PLAYING)  
        
    def pause(self):
        '''
        Pause the pipeline
        '''
        self._camerabin.set_state(Gst.State.PAUSED)
    
    def stop(self):
        '''
        Delete the pipeline
        '''
        self._camerabin.set_state(Gst.State.NULL)
