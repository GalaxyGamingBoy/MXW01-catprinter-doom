import cydoomgeneric as cdg
import catprinter.cmds as cmds
import catprinter.img as imgproc
from catprinter.ble import run_ble
from pynput.keyboard import Key, Listener

import asyncio
import numpy as np

from PIL import Image

KEYMAP = {
    Key.left: cdg.Keys.LEFTARROW,
    Key.right: cdg.Keys.RIGHTARROW,
    Key.up: cdg.Keys.UPARROW,
    Key.down: cdg.Keys.DOWNARROW,
    ',': cdg.Keys.STRAFE_L,
    '.': cdg.Keys.STRAFE_R,
    Key.ctrl: cdg.Keys.FIRE,
    Key.space: cdg.Keys.USE,
    Key.shift: cdg.Keys.RSHIFT,
    Key.enter: cdg.Keys.ENTER,
    Key.esc: cdg.Keys.ESCAPE,
}

resx = cmds.PRINTER_WIDTH_PIXELS
resy = 200
device = "MXW01"
intensity = 0xFF

key_queue = []

def on_press(key):
    global key_queue
    key_queue.append((key, 1))

def on_release(key):
    global key_queue
    key_queue.append((key, 0))

def draw_frame(pixels) -> None:
    img = Image.fromarray(pixels[:, :, [2, 1, 0]])
    img = img.convert("L")
    img = np.array(img)
    img = imgproc.floyd_steinberg_dither(img)

    image_data_buffer = cmds.prepare_image_data_buffer(img)

    asyncio.run(
            run_ble(image_data_buffer, device=device, intensity=intensity)
    )

def get_key():
    global key_queue

    if len(key_queue) == 0:
        return None
    
    (k, p) = key_queue.pop(0)
    if k in KEYMAP:
        return (p, KEYMAP[k])
    if len(k) == 1:
        return (p, ord(k.lower()))
    
    return get_key()

cdg.init(    resx=resx,
             resy=resy,
             draw_frame=draw_frame,
             get_key=get_key)

with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    cdg.main()
    listener.join()

