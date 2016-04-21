'''
Created on 16 Apr 2016

@author: cgueret

Inspired from https://github.com/groakat/UVCH264Capture/blob/master/UVCH264Capture/captureVideo.py
and http://stackoverflow.com/questions/30191622/gstreamer-python-change-filesrc
and https://github.com/gebart/livestream/blob/master/h264-sender.py
and https://github.com/rubenrua/GstreamerCodeSnippets/blob/master/0.10/Python/pygst-sdk-tutorials/basic-tutorial-7.py

'''
import os
from enum import Enum
from datetime import datetime
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst
from gi.repository import GdkX11  # for window.get_xid() @UnusedImport
from gi.repository import GstVideo  # for sink.set_window_handle() @UnusedImport

class CaptureType(Enum):
    png = 'png'
    jpg = 'jpeg'
    
class Camera(object):
    '''
    Wrapper around the camera. Uses gstreamer to build a pipeline that produces
    a first stream going to a view find and another one going to a gdkpixbuf
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Set the format for saving images
        self.capture = CaptureType.jpg
        
        # Set the hardware bits (TODO: detect the hardware)
        isRpi = not os.path.exists('/dev/video1')
        device = '/dev/video0' if isRpi else '/dev/video1'
        self.pipeline = self._build_pipeline(device, isRpi)
        
        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self._on_message)
    
    def _on_message(self, bus, message):
        '''
        Print a message received from Gstreamer
        '''
        if message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print ('Warning: %s' % err, debug)
        
    def bind_view_finder_to_widget(self, widget):
        '''
        Connect the view finder to a Widget
        '''
        xid = widget.get_window().get_xid()
        view_finder = self.pipeline.get_by_name('viewfinder')
        view_finder.set_window_handle(xid)
    
    def _build_pipeline(self, device, isRpi):
        '''
        Create the pipeline for Gstreamer
        
        @param device: the name of the webcam to use
        @param isRpi: True if currently running RPi(2) hardware
        '''  
        # Create the pipeline
        pipeline = Gst.Pipeline.new('camera-pipeline')
        
        # Build the source
        webcam = Gst.ElementFactory.make('v4l2src', 'webcam')
        webcam.set_property('device', device)
        pipeline.add(webcam)
        
        # Add the h264 decoding pipeline
        parser = Gst.ElementFactory.make('h264parse')
        decoder_name = 'omxh264dec' if isRpi else 'avdec_h264'
        print ('Using %s for decoding the h264 stream' % decoder_name)
        decoder = Gst.ElementFactory.make(decoder_name)
        pipeline.add(parser)
        pipeline.add(decoder)
        parser.link(decoder)
        webcam_caps = Gst.Caps.from_string('video/x-h264, width=(int)1920, height=(int)1080, framerate=(fraction)24/1')
        webcam.link_filtered(parser, webcam_caps)
        
        # Split the decoded h264 stream in two
        # First branch streams the video to a view finder
        # Second branch send the content to a GdkPixBuf for saving shots
        tee = Gst.ElementFactory.make('tee', 'splitter')
        pipeline.add(tee)
        decoder.link(tee)
        
        # View finder
        vf_pad = tee.get_request_pad('src_%u')
        print ('Obtained request pad %s for view finder' % vf_pad.get_name())
        vf_queue = Gst.ElementFactory.make('queue')
        vf_flip = Gst.ElementFactory.make('videoflip')
        vf_flip.set_property("method", "horizontal-flip")
        vf_convert = Gst.ElementFactory.make('autovideoconvert')
        vf_scale = Gst.ElementFactory.make('videoscale')
        vf_overlay = Gst.ElementFactory.make('textoverlay', 'timer')
        vf_overlay.set_property('font-desc', 'Ubuntu,Bold 70')
        sink = 'ximagesink' if isRpi else 'glimagesink'
        print ('Connecting a %s sink' % sink)
        vf_sink = Gst.ElementFactory.make(sink, 'viewfinder')
        vf_sink.set_property('sync', False)
        #vf_overlay.set_property('draw-shadow', False)
        #vf_overlay.set_property('draw-outline', False)
        pipeline.add(vf_queue)
        pipeline.add(vf_flip)
        pipeline.add(vf_overlay)
        pipeline.add(vf_convert)
        pipeline.add(vf_scale)
        pipeline.add(vf_sink)
        vf_pad.link(vf_queue.get_static_pad('sink'))
        vf_queue.link(vf_flip)
        vf_flip.link(vf_overlay)
        vf_overlay.link(vf_convert)
        vf_convert.link(vf_scale)
        vf_caps = Gst.Caps.from_string('video/x-raw, width=(int)768, height=(int)576')
        vf_scale.link_filtered(vf_sink, vf_caps)

        # Image capture
        img_pad = tee.get_request_pad('src_%u')
        print ('Obtained request pad %s for image capture' % img_pad.get_name())
        img_queue = Gst.ElementFactory.make('queue')
        img_convert = Gst.ElementFactory.make('autovideoconvert')
        img_pixbuf = Gst.ElementFactory.make('gdkpixbufsink', 'buffer')
        img_pixbuf.set_property('sync', False)
        pipeline.add(img_queue)
        pipeline.add(img_convert)
        pipeline.add(img_pixbuf)
        img_pad.link(img_queue.get_static_pad('sink'))
        img_queue.link(img_convert)
        img_convert.link(img_pixbuf)
                
        # Return the newly built pipeline        
        return pipeline
        
    def take_photo(self):
        '''
        Take a photo
        '''
        os.makedirs('./photos', exist_ok=True)
        
        # Get a timestamp
        d = datetime.now()
        timestamp = d.isoformat(' ').split('.')[0]
        
        # Set the file name
        ext = self.capture.name
        file_name = './photos/{}.{}'.format(timestamp, ext)
        
        # Set the parameters
        parameters = {}
        if self.capture == CaptureType.jpg:
            parameters['quality'] = '98'
        elif self.capture == CaptureType.png:
            parameters['compression'] = '3'
            parameters['tEXt::Title'] = timestamp

        # Save the image
        buffer = self.pipeline.get_by_name('buffer')
        pixbuf = buffer.get_property('last-pixbuf')
        pixbuf.savev(file_name, self.capture.value, 
                     list(parameters.keys()), list(parameters.values()))
        
    def show_count_down(self, value):
        '''
        Show a particular count down value
        '''
        overlay = self.pipeline.get_by_name('timer')
        overlay.set_property('text', value)
        
    def hide_count_down(self):
        '''
        Hide the count down overlay
        '''
        overlay = self.pipeline.get_by_name('timer')
        overlay.set_property('text', '')
        
    def start(self):
        '''
        Start the pipeline
        '''
        self.pipeline.set_state(Gst.State.PLAYING)  
    
    def pause(self):
        '''
        Pause the pipeline
        '''
        self.pipeline.set_state(Gst.State.PAUSED)
    
    def stop(self):
        '''
        Delete the pipeline
        '''
        self.pipeline.set_state(Gst.State.NULL)
    
    
