```
 ____  _                 _      ____                    
/ ___|(_)_ __ ___  _ __ | | ___/ ___| _ __   __ _ _ __  
\___ \| | '_ ` _ \| '_ \| |/ _ \___ \| '_ \ / _` | '_ \ 
 ___) | | | | | | | |_) | |  __/___) | | | | (_| | |_) |
|____/|_|_| |_| |_| .__/|_|\___|____/|_| |_|\__,_| .__/ 
                  |_|                            |_|    
```

A very basic photo booth software using Gstreamer and GTK

Logo by http://www.figlet.org/

# Installation
Starting with a freshly flashed Jessie, add all the dependencies

```
apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0
```

Then increase the video memory to be sure the hardware decoder has all it needs. Add this at the bottom of `/boot/config.txt`

```
gpu_mem=256
```

