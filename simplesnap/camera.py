'''
Created on 16 Apr 2016

@author: cgueret
'''
from gi.overrides.Gtk import Widget

class Camera(object):
    '''
    Wrapper around the camera. Uses gstreamer to build a pipeline that produces
    a first stream going to a view find and another one going to a gdkpixbuf
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def bind_vf_sink_to_widget(self):
        '''
        Connect the view finder to a Widget
        '''
        