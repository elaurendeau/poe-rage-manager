import re
import threading
import time

import win32con
import win32ui
from PIL import ImageGrab
import keyboard

import win32gui

use_withering_step = True

general_cry_key = 0x51
withering_step_key = 0x52
rage_position = (2295, 1205, 2296, 1206)

poe_log_file_path = "C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt"

active = False
in_hideout = False

def tail(file):
    file.seek(0, 2)
    while True:
        line = ""
        try:
            line = file.readline()
        except:
            print("Unable to parse line from file")

        if not line:
            time.sleep(0.1)
            continue

        yield line


def watchFile():
    file = open(poe_log_file_path, "r")
    pattern = ".*: You have entered ([a-zA-Z \']+)\."
    auditlog = tail(file)
    for line in auditlog:
        result = re.match(pattern, line)
        if result:
            global in_hideout
            if "Hideout" in result.group(1):
                in_hideout = True
            else:
                in_hideout = False

def execute():
    toplist, winlist = [], []

    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)
    path_of_exile_application = [(hwnd, title) for hwnd, title in winlist if 'path of exile' in title.lower()]
    # just grab the hwnd for first window matching path_of_exile_application
    path_of_exile_application = path_of_exile_application[0]
    hwnd = path_of_exile_application[0]
    window = win32ui.CreateWindowFromHandle(hwnd)

    skip_withering_step = True
    while active:
        if win32gui.GetForegroundWindow() == hwnd and not in_hideout:
            bbox = win32gui.GetWindowRect(hwnd)
            img = ImageGrab.grab(bbox)
            im1 = img.crop(rage_position)

            if len(im1.getcolors()) == 1:
                value, rgb = im1.getcolors()[0]
                if not (244 > rgb[0] > 234 and 69 > rgb[1] > 59 and 65 > rgb[2] > 55) and not keyboard.is_pressed('ctrl'):
                    window.SendMessage(win32con.WM_KEYDOWN, general_cry_key, 0)
                    time.sleep(0.1)
                    window.SendMessage(win32con.WM_KEYUP, general_cry_key, 0)

            if use_withering_step and skip_withering_step and not keyboard.is_pressed('ctrl'):
                window.SendMessage(win32con.WM_KEYDOWN, withering_step_key, 0)
                time.sleep(0.1)
                window.SendMessage(win32con.WM_KEYUP, withering_step_key, 0)

        skip_withering_step = not skip_withering_step
        time.sleep(0.2)


if __name__ == "__main__":
    active = not active

    b = threading.Thread(name='background', target=watchFile)
    f = threading.Thread(name='foreground', target=execute)

    b.start()
    f.start()
