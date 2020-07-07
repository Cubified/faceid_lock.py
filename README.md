# faceid\_lock.py

A facial recognition lockscreen for X11.  Not recommended for use in security-sensitive situations, but still a fun tinker toy.  This is the Python-only version of [this repository](https://github.com/Cubified/faceid_lock), bringing increased customizability, speed, and user-friendliness.

## Screenshots

![Screenshot 1](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot1.png)

![Screenshot 2](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot2.png)

![Screenshot 3](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot3.png)

![Screenshot 4](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot4.png)

## Dependencies

- Python 3:
  - [face_recognition](https://github.com/ageitgey/face_recognition)
  - _If using with Kinect_: [`libfreenect`](https://github.com/openkinect/libfreenect)
    - Compiled with support for the Python 3 wrapper (`-DBUILD_PYTHON3=ON` passed as argument to cmake)
  - _If using with webcam_: [OpenCV](https://opencv.org)
  - [`python-xlib`](https://github.com/python-xlib/python-xlib)
- A webcam or Microsoft Kinect (tested with original version for XB360)

## Running

Assuming all dependencies have been installed properly (which unfortunately cannot be done with a `requirements.txt` due to freenect not being a `pip` package), simply run:

     $ ./faceid_lock.py

To ensure that everything has installed successfully.  It should return an error (as it will have been unable to find the `user_image` file required for facial recognition) while also creating the `faceid_lock` configuration directory in `~/.local/share`.  To configure and run properly, see below.

## Configuration

Upon first run, `faceid_lock.py` should create a `conf.ini` file in `~/.local/share/faceid_lock` which contains a barebones example of a configuration file.  `faceid_lock.py` can be configured further as follows:

```ini
[example_rectangle]                  ; Section name, can be anything but must be unique
type = rectangle                     ; Required
x = 10                               ; Required
y = 10                               ; Required
w = 100                              ; Required
h = 50                               ; Required
color = [rgb:ff/12/34 | red]         ; X11-style color triple or color name
image = /path/to/image_file.png      ; A path to an image in any common format
fit_image = true                     ; Resize image to fit width and height specified earlier (does not respect aspect ratio)

[example_text]                       ; Section name, can be anything but must be unique
type = text                          ; Required
x = 20                               ; Required
y = 20                               ; Required
font = -*-*-*-*-*-*-12-*-*-*-*-*-*-* ; X11-style font selector, use xlsfonts or xfontsel to view choices
                                     ; One of the following three is required
text = hello world                   ; String literal to be printed
text = STATUS                        ; User-friendly status text (e.g. "Setting up...," "Checking...," "Face not recognized.")
command = date                       ; Command to be executed on redraw, output is printed

[X]                                  ; Section entitled X affects entire screen, all keys are optional
color = [rgb:33/33/33 | gray]        ; X11 color triple or color name
background = /path/to/background.png ; An image file to be placed in the background, can be in any common format
fit_image = true                     ; Whether the background image should be scaled to fit the entire screen

[facial_rec]                         ; All keys in this section are required
user_image = /path/to/user_image     ; Path to an image of the user's face, can be in any common format
webcam = [kinect | cv]               ; Webcam backend to use, kinect will use freenect while cv will use OpenCV
```

- `[X]` Section:
  - `background`: A path to a background image
  - `box_{x, y}`: The {x, y} position of the text background box
  - `box_{w, h}`: The {width, height} of the text background box
  - `text_{x, y}`: The {x, y} position of the status text
  - `{text, box}_color`: The color of the onscreen {text, background box}
- `[facial_rec]` Section:
  - `user_image`: A path to an image containing the user's face
  - `webcam`: Webcam backend to use, either `kinect` or `cv`

## Installing

Although there exists no automatic way to install this script, this can be achieved through:

     $ cp faceid_lock.py ~/.local/bin

## To-Do

- Cache background images to avoid slight lag on redraw
- Transparency
- Text centering
- More input backends than solely face?
