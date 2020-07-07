#!/usr/bin/python3

##############################
# faceid_lock.py: a facial
# recognition lock for X11
#

import os
import io
import argparse
import configparser

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
    'background': default_configdir+'/background.png',
    'box_x': '20',
    'box_y': '1010',
    'box_w': '150',
    'box_h': '50',
    'text_x': '30',
    'text_y': '1038',
    'text_color': 'black',
    'box_color': 'white'
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
from Xlib import X, display, Xcursorfont
from PIL import Image

def disp(dpy, win, gc, fg, bg, msg):
    gc.change(
        foreground=bg
    )
    win.fill_rectangle(
        gc,
        int(config['X']['box_x']), int(config['X']['box_y']),
        int(config['X']['box_w']), int(config['X']['box_h'])
    )
    gc.change(
        foreground=fg
    )
    win.draw_text(gc, int(config['X']['text_x']), int(config['X']['text_y']), msg)

def init():
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
    try:
        bgd_img = Image.open(os.path.expanduser(config['X']['background']))
    except FileNotFoundError:
        print('Warning: background image "'+os.path.expanduser(config['X']['background'])+'" not found.')
        bgd_img = Image.new("RGB", (scr.width_in_pixels, scr.height_in_pixels))
    else:
        bgd_img = bgd_img.convert(mode="RGB")

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

    cmap = scr.default_colormap
    fg = cmap.alloc_named_color(config['X']['text_color'])
    bg = cmap.alloc_named_color(config['X']['box_color'])
    if fg == None or bg == None:
        print('Warning: unrecognized text and/or box colors "'+config['X']['text_color']+'" and "'+config['X']['box_color']+'".')
        fg = scr.black_pixel
        bg = scr.white_pixel
    else:
        fg = fg.pixel
        bg = bg.pixel

    win.set_wm_name('faceid_lock')
    win.map()
    win.put_pil_image(gc, 0, 0, bgd_img)
    disp(dpy, win, gc, fg, bg, 'Setting up...')
    dpy.sync()

    return {
        'dpy': dpy,
        'win': win,
        'gc':  gc,
        'fg':  fg,
        'bg':  bg
    }

def loop(dpy, win, gc, fg, bg):
    evt = dpy.next_event()
    if evt.type == X.ButtonPress and evt.detail == 1:
        disp(dpy, win, gc, fg, bg, 'Checking...')
        dpy.sync()
        out = check_face()
        if out == 'success':
            dpy.ungrab_pointer(0)
            dpy.ungrab_keyboard(0)
            win.unmap()
            dpy.close()
            exit(0)
        else:
            disp(dpy, win, gc, fg, bg, out)
    loop(dpy, win, gc, fg, bg)

x_vars = init()

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
    if config['facial_rec']['webcam'] == 'kinect':
        img = freenect.sync_get_video()[0]
    else:
        cap = cv2.VideoCapture(0)
        ret, img = cap.read()
        cap.release()
    if img.size == 0:
        return 'Webcam error.'
    all_enc = face_recognition.face_encodings(img)
    if(len(all_enc) > 0):
        new = all_enc[0]
        sim = face_recognition.compare_faces([enc],new)
        if True in sim:
            return 'success'
        else:
            return 'Face not recognized.'
    else:
        return 'No faces detected.'

##############################
# Event listener loop
#
disp(x_vars['dpy'], x_vars['win'], x_vars['gc'], x_vars['fg'], x_vars['bg'], 'Click to unlock.')
loop(**x_vars)
