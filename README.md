# faceid\_lock.py

A facial recognition lockscreen for X11.  Not recommended for use in security-sensitive situations, but still a fun tinker toy.  This is the Python-only version of [this repository](https://github.com/Cubified/faceid_lock), bringing increased customizability and user-friendliness.

## Screenshots

![Screenshot 1](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot1.png)

![Screenshot 2](https://github.com/Cubified/faceid_lock.py/blob/master/screenshot2.png)

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

To ensure that everything has installed successfully.  It should return an error while also creating the `faceid_lock` configuration directory in `~/.local/share` where an image named `user_image` must be present.  This image can be in any common file format (JPG, PNG, etc.).

## Configuration

Upon first run, `faceid_lock.py` should create a `conf.ini` file in `~/.local/share/faceid_lock` which contains all available configuration options.  Specifically, these are:

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
