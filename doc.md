http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.pdf
http://wiki.oz9aec.net/index.php/Gstreamer_cheat_sheet#Text_Overlay
http://stackoverflow.com/questions/3139747/python-gstreamer-webcam-viewer
http://wiki.pitivi.org/wiki/PyGST_Tutorial/Getting_Started

gst-launch-1.0 v4l2src ! aasink sync=false

https://lazka.github.io/pgi-docs/Gst-1.0/structs/Caps.html
https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-bad-libs/html/index.html

http://kakaroto.homelinux.net/2012/09/uvc-h264-encoding-cameras-support-in-gstreamer/

gst-launch-1.0 -v -e uvch264src device=/dev/video1 name=src auto-start=true \
src.vfsrc ! queue ! video/x-raw,format=\(string\)BGRA,width=320,height=240,framerate=30/1 ! gtksink sync=false \
src.vidsrc ! queue ! video/x-h264,width=1920,height=1080,framerate=10/1 ! h264parse ! avdec_h264 ! autovideoconvert ! gtksink sync=false

gst-launch-1.0 -v -e v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1280,height=720,framerate=5/1 ! h264parse ! avdec_h264 ! autovideoconvert ! gdkpixbufsink sync=false

pipeline = "v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! avdec_h264 ! autovideoconvert ! videoscale ! capsfilter ! gtksink name=gtk sync=false"

        
gst-launch-1.0 -v -e v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1280,height=720,framerate=5/1 ! h264parse ! avdec_h264 ! tee name=t ! queue ! autovideoconvert ! gtksink t. ! queue ! autovideoconvert ! gdkpixbufsink sync=false
gst-launch-1.0 -v -e v4l2src device=/dev/video1 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! avdec_h264 ! tee name=t ! queue ! autovideoconvert ! videoscale ! video/x-raw,width=640,height=480 ! ximagesink t. ! queue ! autovideoconvert ! gdkpixbufsink sync=false

# Working on the Pi

Also uses hardware decoding

```
gst-launch-1.0 -v -e v4l2src device=/dev/video0 ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! omxh264dec ! tee name=t ! queue ! autovideoconvert ! videoscale ! video/x-raw,width=320,height=240 ! ximagesink sync=false t.  ! queue ! autovideoconvert ! gdkpixbufsink sync=false
```
