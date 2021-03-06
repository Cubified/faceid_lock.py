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
  - _If using with password_: [`python-pam`](https://github.com/FirefighterBlu3/python-pam)
  - [`python-xlib`](https://github.com/python-xlib/python-xlib)
- A webcam or Microsoft Kinect (tested with original version for XB360)

## Running

Assuming all dependencies have been installed properly (which unfortunately cannot be done with a `requirements.txt` due to freenect not being a `pip` package), simply run:

     $ ./faceid_lock.py --test

To ensure that everything has installed successfully.  It should open a black window while also creating the `faceid_lock` configuration directory in `~/.local/share`.  Control+C from the terminal can be used to close this, or the user's password can be entered within the window itself.  To configure and run properly, see below.

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
                                     ; One of the following is required
text = hello world                   ; String literal to be printed
text = STATUS                        ; User-friendly status text (e.g. "Setting up...," "Checking...," "Face not recognized.")
text = INPUT                         ; If using the password authentication backend (see below), a masked (asterisked) string of user input
command = date                       ; Command to be executed on redraw, output is printed

[X]                                  ; Section entitled X affects entire screen, all keys are optional
color = [rgb:33/33/33 | gray]        ; X11 color triple or color name
background = /path/to/background.png ; An image file to be placed in the background, can be in any common format
fit_image = true                     ; Whether the background image should be scaled to fit the entire screen

[auth]                               ; If using the "facial_rec" backend, all keys are required -- if not, only the "backend" key is required
backend = [facial_rec | password]    ; Authentication backend to use
user_image = /path/to/user_image     ; Path to an image of the user's face, can be in any common format (facial_rec backend only)
webcam = [kinect | cv]               ; Webcam backend to use, kinect will use freenect while cv will use OpenCV (facial_rec backend only)
```

## Installing

Although there exists no automatic way to install this script, this can be achieved through:

     $ cp faceid_lock.py ~/.local/bin

## To-Do

- ~~Cache background images to avoid slight lag on redraw~~
  - Update: Xlib's `put_pil_image`, not PIL image operations, are the cause of lag, meaning caching has little to no effect on responsiveness (although it does reduce disk usage)
- Transparency (likely already possible with a compositor)
- Text centering (`python-xlib` does not support XTextExtents, not possible without overly complex logic)
- Fix PIL Image.resize creating black border on bottom when aspect ratio does not match
