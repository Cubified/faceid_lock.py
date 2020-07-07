#!/usr/bin/python3

##############################
# faceid_lock.py: a facial
# recognition lock for X11
#
import os
import io
import argparse
import configparser
import subprocess

parser = argparse.ArgumentParser(description='Lock the current X display.')
parser.add_argument('--config', metavar='conf.ini', type=str, help='a config file to read (default is ~/.local/share/faceid_lock/conf.ini)')
parser.add_argument('--test', action='store_true', help='run in test mode (does not lock screen)')

args = parser.parse_args()

if args.test:
    print('Running in test mode.')

default_configdir = os.path.expanduser('~/.local/share/faceid_lock')
default_configfile = default_configdir+'/conf.ini'
config = configparser.ConfigParser()
config['X'] = {
    'color': 'rgb:00/00/00'
}
config['facial_rec'] = {
    'user_image': default_configdir+'/user_image',
    'webcam': 'kinect'
}

if len(config.read(default_configfile)) == 0:
    print('Default config file "'+default_configfile+'" does not exist, creating.')
    os.makedirs(default_configdir)
    with open(default_configfile, 'w') as configfile:
        config.write(configfile)

if not args.config == None:
    try:
        config.read(args.config)
    except FileNotFoundError:
        print('Warning: config file "'+args.config+'", does not exist, loading defaults.')

##############################
# X Window
#
# (Catches display error
#  before loading face_rec)
#
from Xlib import X, display, Xcursorfont
from PIL import Image
# import numpy as np

status = 'Setting up...'
# cam_data = np.asarray([0])

def x_draw_rect(dpy, win, gc, dict, verify_params=True):
    if verify_params:
        if not ('x' in dict and
                'y' in dict and
                'w' in dict and
                'h' in dict):
            print('Warning: rectangle definition must contain at least x, y, w, and h values.')
            return
    else:
        dict['x'] = '0'
        dict['y'] = '0'
        dict['w'] = str(dpy.screen().width_in_pixels)
        dict['h'] = str(dpy.screen().height_in_pixels)
        if 'background' in dict:
            dict['image'] = dict['background']

    if 'color' in dict:
        cmap = dpy.screen().default_colormap
        color = cmap.alloc_named_color(dict['color'])
        if not color == None:
            gc.change(
                foreground=color.pixel
            )
            win.fill_rectangle(
                gc,
                int(dict['x']), int(dict['y']),
                int(dict['w']), int(dict['h']),
            )
        else:
            print('Warning: unrecognized color "'+dict['color']+'" in rectangle definition.')
    
    if 'image' in dict:
        try:
            bgd_img = Image.open(os.path.expanduser(dict['image']))
        except FileNotFoundError:
            print('Warning: image "'+os.path.expanduser(dict['image'])+'" in rectangle definition not found.')
        else:
            bgd_img = bgd_img.convert(mode="RGB")
            if('fit_image' in dict and
               dict['fit_image'] == 'true'):
                bgd_img = bgd_img.resize((int(dict['w']), int(dict['h'])))
            win.put_pil_image(gc, 0, 0, bgd_img)
    
def x_draw_text(dpy, win, gc, dict):
    if not ('x' in dict and
            'y' in dict and
           ('text' in dict or
            'command' in dict)):
        print('Warning: text definition must contain at least x and y values, and one of either text or command values.')
        return

    gc.change(
        foreground=dpy.screen().black_pixel
    )

    if 'font' in dict:
        font = dpy.open_font(dict['font'])
        if not font == None:
            gc.change(
                font=font
            )
        else:
            print('Warning: font "'+dict['font']+'" not found.')

    if 'color' in dict:
        cmap = dpy.screen().default_colormap
        color = cmap.alloc_named_color(dict['color'])
        if not color == None:
            gc.change(
                foreground=color.pixel
            )
            if 'command' in dict:
                string = subprocess.check_output(['sh', '-c', dict['command']])
            else:
                if dict['text'] == 'STATUS':
                    global status
                    string = status
                else:
                    string = dict['text']

            win.draw_text(
                gc,
                int(dict['x']), int(dict['y']),
                string
            )
        else:
            print('Warning: unrecognized color "'+dict['color']+'" in text definition.')

"""
This is quite lag-heavy and largely useless, as the image is only painted on mouse click.

All other commented lines allow this to work, however until I go about optimizing this
I will leave it commented out

def x_draw_cam(dpy, win, gc, dict):
    if not ('x' in dict and
            'y' in dict and
            'w' in dict and
            'h' in dict):
        print('Warning: webcam definition must contain at least x, y, w, and h values.')
        return
    
    global cam_data

    try:
        win.put_pil_image(
            gc,
            int(dict['x']), int(dict['y']),
            Image.fromarray(cam_data)
                 .resize(
                    (int(dict['w']), int(dict['h']))
                 )
        )
    except TypeError:
        pass
"""

def x_draw(dpy, win, gc, buf, buf_gc):
    if 'X' in config:
        x_draw_rect(dpy, buf, buf_gc, config['X'], verify_params=False)
    for key in config:
        if 'type' in config[key]:
            if config[key]['type'] == 'rectangle':
                x_draw_rect(dpy, buf, buf_gc, config[key])
            elif config[key]['type'] == 'text':
                x_draw_text(dpy, buf, buf_gc, config[key])
#            elif config[key]['type'] == 'webcam':
#                x_draw_cam(dpy, buf, buf_gc, config[key])
    win.copy_area(
        gc,
        buf,
        0, 0,
        dpy.screen().width_in_pixels, dpy.screen().height_in_pixels,
        0, 0
    )

def x_init():
    dpy = display.Display()
    scr = dpy.screen()
    win = scr.root.create_window(
        0, 0,
        scr.width_in_pixels, scr.height_in_pixels,
        0, scr.root_depth,
        X.InputOutput,
        X.CopyFromParent,
        background_pixel = scr.black_pixel,
        override_redirect = not args.test,
        event_mask = X.ButtonPressMask,
        colormap = X.CopyFromParent
    )
    gc = win.create_gc()
    buf = win.create_pixmap(
        scr.width_in_pixels,
        scr.height_in_pixels,
        scr.root_depth
    )
    buf_gc = buf.create_gc()

    if not args.test:
        scr.root.grab_pointer(
            win,
            X.ButtonPressMask,
            X.GrabModeAsync,
            X.GrabModeAsync,
            X.NONE,
            X.NONE,
            X.CurrentTime
        )
        scr.root.grab_keyboard(
            win,
            X.GrabModeAsync,
            X.GrabModeAsync,
            X.CurrentTime
        )

    win.map()
    x_draw(dpy, win, gc, buf, buf_gc)
    dpy.sync()

    return {
        'dpy': dpy,
        'win': win,
        'gc':  gc,
        'buf': buf,
        'buf_gc': buf_gc
    }

def x_loop(dpy, win, gc, buf, buf_gc):
    evt = dpy.next_event()
    if evt.type == X.ButtonPress and evt.detail == 1:
        global status
        status = 'Checking...'
        x_draw(dpy, win, gc, buf, buf_gc)
        dpy.sync()

        out = check_face()
        if out:
            dpy.ungrab_pointer(0)
            dpy.ungrab_keyboard(0)
            win.unmap()
            buf.free()
            win.destroy()
            dpy.close()
            exit(0)
        else:
            x_draw(dpy, win, gc, buf, buf_gc)
    x_loop(dpy, win, gc, buf, buf_gc)

##############################
# Entry point
#
x_vars = x_init()

##############################
# Facial rec (heavy includes,
# show window before
# importing)
#
import face_recognition
if config['facial_rec']['webcam'] == 'kinect':
    import freenect
else:
    import cv2

try:
    enc = face_recognition.face_encodings(face_recognition.load_image_file(config['facial_rec']['user_image']))[0]
except FileNotFoundError:
    print('Error: User image file "'+config['facial_rec']['user_image']+'" not found, exiting.')
    exit(1)

def check_face():
    global status
#    global cam_data

    if config['facial_rec']['webcam'] == 'kinect':
        img = freenect.sync_get_video()[0]
    else:
        cap = cv2.VideoCapture(0)
        ret, img = cap.read()
        cap.release()

    if img.size == 0:
        status = 'Webcam error.'
        return 0

#    cam_data = img

    all_enc = face_recognition.face_encodings(img)
    if(len(all_enc) > 0):
        new = all_enc[0]
        sim = face_recognition.compare_faces([enc],new)
        if not True in sim:
            status = 'Face not recognized.'
            return 0
        return 1
    else:
        status = 'No faces detected.'
        return 0

##############################
# Event listener loop
#
status = 'Click to unlock.'
x_draw(**x_vars)
x_loop(**x_vars)
