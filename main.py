import copy
import math
import os
import time
from collections import OrderedDict
from itertools import combinations

import hitherdither
import numpy as np
import pyautogui
import pynput
from PIL import Image
from wand.image import Image as WandImage
# from colour import Color
from pynput import keyboard, mouse

from common import *

muis = pynput.mouse.Controller()


def delay():
    time.sleep(1 / 240)


def wait_for_click() -> mouse.Events.Click:
    with mouse.Events() as events:
        # Block at most one second
        while True:
            event = events.get()
            if isinstance(event, mouse.Events.Click) and event.pressed:
                return event


def wait_for_unclick() -> mouse.Events.Click:
    with mouse.Events() as events:
        # Block at most one second
        while True:
            event = events.get()
            if isinstance(event, mouse.Events.Click) and not event.pressed:
                return event


def click_pos():
    e = wait_for_click()
    return Coordinate(x=e.x, y=e.y)


def wait_for_key() -> keyboard.Events.Press:
    with keyboard.Events() as events:
        while True:
            event = events.get()
            if isinstance(event, keyboard.Events.Press):
                return event


def intput(msg, default=None):
    i = input(f"{msg}\n").strip()
    if i:
        return int(i)
    else:
        return default


def startmsg():
    print("Press any key (except q) to begin.")
    wait_for_key()


def canvas_calibration():
    global top_left, bottom_right, tall, wide
    print("Canvas calibration:")
    print("Click the top left corner.")
    top_left = click_pos()
    print(top_left)
    print("Click the bottom right corner.")
    bottom_right = click_pos()
    print(bottom_right)
    tall = intput("How many pixels TALL is your canvas? (small is 16, large is 32)", 32)
    wide = intput("How many pixels WIDE is your canvas? (small is 16, large is 32)", 32)
    print(f"{tall}x{wide} canvas")


def color_calibration():
    global colors, col_count, palette
    print("Color calibration: ")
    colors = OrderedDict()
    col_count = intput("How many colors does your palette have? (default 16)", 16)
    for i in range(col_count):
        print(f"Color {i + 1}/{col_count}:")
        print("Click the color on the palette (THE BACKGROUND, NOT THE DYE ICON!!)")
        pos = click_pos()
        wait_for_unclick()
        muis.position = (pos.x + 500, pos.y)
        print(pos)
        time.sleep(0.5)
        muis.position = (pos.x + 500, pos.y)
        col = pyautogui.pixel(pos.x, pos.y)
        col = Color(r=col[0], g=col[1], b=col[2])
        muis.position = (pos.x, pos.y)

        print(f"{col} at {pos}")
        colors[col] = pos
    palette = list(colors.keys())
    print(colors)
    print(palette)


# ripped and converted from JoP mod
def mix(a: Color, b: Color, ratio: float) -> Color:
    if ratio == 1.0:
        return a
    elif ratio == 0.0:
        return b

    # would you shut up python? its all colors, floor returns a color, die
    res: Color = math.floor(a * ratio) + math.floor(b * (1 - ratio))

    average_maximum = int(max(a.r, a.g, a.b) * ratio) + int(max(b.r, b.g, b.b) * (1 - ratio))
    maximum_of_average = max(res.r, res.g, res.b)
    gain_factor = 0 if maximum_of_average == 0 else average_maximum // maximum_of_average

    res *= gain_factor

    return res


def mix_calibration():
    global opacities, mixer, mix_slot, water_slot
    opacities = OrderedDict()
    for opacity in [1.0, 0.75, 0.5]:  # , 0.25]:
        print(f"Click the {int(opacity * 100)}% opacity icon.")
        pos = click_pos()
        opacities[opacity] = pos
    print(opacities)
    print("Click on the eyedropper")
    mixer = click_pos()
    print("Click on any open custom palette slot")
    mix_slot = click_pos()
    print("Click on the water slot")
    water_slot = click_pos()




def mix_calculation():
    global colors, e_palette, palette
    e_palette = OrderedDict()
    for color, pos in colors.items():
        e_palette[color] = JoPPureColor(color=color, position=pos)

    first_e_palette = list(e_palette.values()).copy()

    for depth in range(3):
        for mixcol in list(e_palette.values()).copy():
            for palcol in first_e_palette:
                for opacity in [0.5, 0.75]:
                    new_col = mix(palcol.color, mixcol.color, opacity)
                    if new_col not in e_palette:
                        e_palette[new_col] = JoPMixedColor(color=new_col, color1=palcol,
                                                           color2=mixcol, opacity=opacity)
        print(f"combination search depth {depth}")
    print(f"{len(e_palette)} colors found")

def save_calibration():
    print("saving...")
    with open("savedcalibration.py", "w+") as f:
        f.write("from collections import OrderedDict\nfrom common import *\n\n")
        for var in ["tall", "wide", "top_left", "bottom_right", "col_count", "colors", "opacities", "mixer",
                    "mix_slot", "water_slot"]:
            f.write(f"{var} = {globals()[var]}\n")
    print("calibration saved!")


def all_defined(*names: str):
    return all([name in globals() for name in names])


def click(pos: tuple | Coordinate):
    if isinstance(pos, tuple):
        (x, y) = pos
    else:
        (x, y) = (pos.x, pos.y)
    muis.position = (x, y)
    delay()
    muis.click(mouse.Button.left)
    delay()


# stupid value so it always sets on first go, i keep forgtetting
current_opacity = -1.0


def set_opacity(o: float):
    global current_opacity
    if current_opacity != o:
        click(opacities[o])
        current_opacity = o


def drag_between(frm: Coordinate, to: Coordinate):
    muis.position = (frm.x, frm.y)
    delay()
    muis.press(mouse.Button.left)
    delay()
    muis.position = (to.x, to.y)
    delay()
    muis.release(mouse.Button.left)
    delay()


def click_color(color: JoPColor, so=True):
    if isinstance(color, JoPPureColor):
        if so:
            set_opacity(1.0)
        click(color.position)
    elif isinstance(color, JoPMixedColor):
        # if isinstance(color.color1, JoPMixedColor) or isinstance(color.color2, JoPMixedColor):
        #     raise NotImplementedError("nested mixing not implemented")
        # mix colors
        set_opacity(1.0)
        click_color(color.color2)
        click(bottom_right)

        set_opacity(color.opacity)
        click_color(color.color1, False)
        click(bottom_right)

        # pick up color
        drag_between(water_slot, mix_slot)
        click(mixer)
        drag_between(bottom_right, mix_slot)
        set_opacity(1.0)
        # new color is autoselected


def main():
    print("Auto \"Joy of Painting\" Script by Machine on a Mission.\nPress q to quit.")

    did_calibration = False
    did_key = False

    if not all_defined("tall", "wide", "top_left", "bottom_right"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        canvas_calibration()
        did_calibration = True

    if not all_defined("col_count", "colors"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        color_calibration()
        did_calibration = True

    if not all_defined("opacities", "mixer", "mix_slot", "water_slot"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        mix_calibration()
        did_calibration = True

    # name = input("Input the filename of the image:\n").strip()
    name = "loki.jpg"

    if True: #did_calibration and input(
            #"type `y` to save calibration, or anything else to not, then press enter.\n").strip() == "y":
        save_calibration()

    canvas_w = 1 # intput("How many canvases wide?", 1)
    canvas_h = 1 # intput("How many canvases tall?", 1)
    print(f"{canvas_w * canvas_h} canvases")

    mix_calculation()

    # tall = 32
    # wide = 32
    # col_count = 28
    # colors = {(249, 255, 254): Coordinate({'y': 482, 'x': 789}), (71, 79, 82): Coordinate({'y': 349, 'x': 769}), (157, 157, 151): Coordinate({'y': 360, 'x': 606}), (249, 128, 29): Coordinate({'y': 502, 'x': 625}), (199, 78, 189): Coordinate({'y': 544, 'x': 490}), (22, 156, 156): Coordinate({'y': 396, 'x': 487}), (137, 50, 184): Coordinate({'y': 469, 'x': 387}), (60, 68, 170): Coordinate({'y': 537, 'x': 334}), (58, 179, 218): Coordinate({'y': 612, 'x': 460}), (131, 84, 50): Coordinate({'y': 643, 'x': 265}), (254, 216, 61): Coordinate({'y': 757, 'x': 427}), (94, 124, 22): Coordinate({'y': 858, 'x': 258}), (128, 199, 31): Coordinate({'y': 913, 'x': 395}), (176, 46, 38): Coordinate({'y': 1011, 'x': 271}), (243, 139, 170): Coordinate({'y': 1044, 'x': 419}), (29, 29, 33): Coordinate({'y': 1129, 'x': 295}), (23, 124, 125): Coordinate({'y': 568, 'x': 805}), (193, 103, 29): Coordinate({'y': 539, 'x': 887}), (156, 65, 149): Coordinate({'y': 636, 'x': 889}), (109, 44, 146): Coordinate({'y': 654, 'x': 789}), (52, 58, 135): Coordinate({'y': 746, 'x': 793}), (50, 141, 171): Coordinate({'y': 720, 'x': 868}), (197, 169, 53): Coordinate({'y': 809, 'x': 841}), (105, 70, 45): Coordinate({'y': 810, 'x': 756}), (103, 156, 31): Coordinate({'y': 894, 'x': 810}), (189, 111, 135): Coordinate({'y': 961, 'x': 748}), (77, 100, 24): Coordinate({'y': 900, 'x': 682}), (139, 41, 36): Coordinate({'y': 995, 'x': 663})}
    # top_left = Coordinate({'y': 251, 'x': 1175})
    # bottom_right = Coordinate({'y': 1020, 'x': 1947})

    delta = bottom_right - top_left

    with WandImage(filename=name) as img:
        img.type = "truecolor"
        # img = img.convert("RGB")
        img.resize(wide * canvas_w, tall * canvas_h)

        hpal = []
        for color in e_palette.keys():
            hpal.append((color.r, color.g, color.b))

        arr = np.array(hpal, dtype=np.uint8)  # shape (N, 3)
        n = len(hpal)
        with WandImage(width=n, height=1) as palette:
            palette.type = "truecolor"
            palette.import_pixels(
                x=0, y=0,
                width=n, height=1,
                channel_map="RGB",
                storage="char",
                data=arr.tobytes()
            )
            palette.save(filename="PNG24:palette.png")
            img.remap(affinity=palette, method='riemersma')#, method="floyd_steinberg")

            # Force the output type to truecolor (RGB) to drop alpha or indexing
            # img.type = 'truecolor'
            img.save(filename="PNG24:out.png")
        # img = img.convert("RGB")
            c_count = 0
            for canvas_wi in range(canvas_w):
                for canvas_hi in range(canvas_h):
                    c_count += 1
                    print(f"canvas at ({canvas_wi}, {canvas_hi}) ({c_count} / {canvas_w * canvas_h})")
                    input(f"press enter on the console when ready (canvas open)")
                    startmsg()
                    print((canvas_wi * wide,
                           canvas_hi * tall,
                           (canvas_wi * wide) + wide,
                           (canvas_hi * tall) + tall))
                    # TODO wrong
                    # img.crop(canvas_wi * wide,
                    #                  canvas_hi * tall,
                    #                  (canvas_wi * wide) + wide,
                    #                  (canvas_hi * tall) + tall)
                    # crop.show()
                    w, h = img.width, img.height
                    flat = img.export_pixels(x=0, y=0, width=w, height=h, channel_map="RGB", storage="char")
                    pixels = np.array(flat, dtype=np.uint8).reshape(h, w, 3)
                    last_col = Color(r=255, g=255, b=255)
                    for x in range(wide):
                        for y in range(tall):
                            # print(x,y)
                            target_px = pixels[x, y]
                            print(target_px)
                            col = Color(r=target_px[0], g=target_px[1], b=target_px[2])
                            # click on palette
                            palette_entry = e_palette[col]
                            if last_col != col:
                                click_color(palette_entry)
                            last_col = col

                            # click on canvas

                            pixel_pos = top_left + Coordinate(x=delta.x * (x / 31), y=delta.y * (y / 31))
                            click(pixel_pos)

    time.sleep(1)
    # img.show()


# early term on q handler
def on_press(key):
    try:
        if key.char == "q":
            os._exit(1)
    except AttributeError:
        pass


listener = keyboard.Listener(on_press=on_press)
listener.start()

# i fucking love storing python data as
# if input("type `y` to load saved calibration, or anything else to not, then press enter.\n").strip() == "y":
from savedcalibration import *

main()
