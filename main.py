import math
import os
import time
from itertools import combinations

import pyautogui
import pynput
from PIL import Image
# from colour import Color
from pynput import keyboard, mouse

from common import *

muis = pynput.mouse.Controller()


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
    colors = {}
    col_count = intput("How many colors does your palette have? (default 16)", 16)
    for i in range(col_count):
        print(f"Color {i + 1}/{col_count}:")
        print("Click the color on the palette (THE BACKGROUND, NOT THE DYE ICON!!)")
        pos = click_pos()
        wait_for_unclick()
        print(pos)
        time.sleep(0.5)
        col = pyautogui.pixel(pos.x, pos.y)
        col = Color(r=col[0], g=col[1], b=col[2])
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
    global opacities, mixer
    opacities = {}
    for opacity in [1.0, 0.75, 0.5, 0.25]:
        print(f"Click the {int(opacity * 100)}% opacity icon.")
        pos = click_pos()
        opacities[opacity] = pos
    print(opacities)
    print("Click on the eyedropper")
    pos = click_pos()
    mixer = pos


e_palette: dict[Color, JoPColor]


def mix_calculation():
    global colors, e_palette, palette
    e_palette = {}
    for color, pos in colors.items():
        e_palette[color] = JoPPureColor(color=color, position=pos)

    for col1, col2 in combinations(e_palette.values(), 2):
        col1: JoPColor
        col2: JoPColor
        for opacity in [0.25, 0.5, 0.75]:
            new_col = mix(col1.color, col2.color, opacity)
            if new_col not in e_palette:
                e_palette[new_col] = JoPMixedColor(color=new_col, color1=col1, color2=col2, opacity=opacity)

    print(e_palette)
    print(len(e_palette.keys()))


def save_calibration():
    print("saving...")
    with open("savedcalibration.py", "w+") as f:
        f.write("from common import *\n\n")
        for var in ["tall", "wide", "top_left", "bottom_right", "col_count", "colors", "opacities", "mixer"]:
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
    muis.click(mouse.Button.left)
    time.sleep(1 / 100)


def click_color(color: JoPColor):
    if isinstance(color, JoPPureColor):
        click(color.position)
    elif isinstance(color, JoPMixedColor):
        if isinstance(color.color1, JoPMixedColor) or isinstance(color.color2, JoPMixedColor):
            raise NotImplementedError("nested mixing not implemented")
        click_color(color.color1)
        click(bottom_right)
        click(opacities[color.opacity])
        click_color(color.color2)
        click(bottom_right)
        muis.position = (mixer.x, mixer.y)
        muis.press(mouse.Button.left)
        time.sleep(1 / 100)
        muis.position = (bottom_right.x, bottom_right.y)
        muis.release(mouse.Button.left)
        time.sleep(1 / 100)


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

    if not all_defined("opacities", "mixer"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        mix_calibration()
        did_calibration = True

    name = input("Input the filename of the image:\n").strip()

    if did_calibration and input(
            "type `y` to save calibration, or anything else to not, then press enter.\n").strip() == "y":
        save_calibration()

    mix_calculation()

    startmsg()

    # tall = 32
    # wide = 32
    # col_count = 28
    # colors = {(249, 255, 254): Coordinate({'y': 482, 'x': 789}), (71, 79, 82): Coordinate({'y': 349, 'x': 769}), (157, 157, 151): Coordinate({'y': 360, 'x': 606}), (249, 128, 29): Coordinate({'y': 502, 'x': 625}), (199, 78, 189): Coordinate({'y': 544, 'x': 490}), (22, 156, 156): Coordinate({'y': 396, 'x': 487}), (137, 50, 184): Coordinate({'y': 469, 'x': 387}), (60, 68, 170): Coordinate({'y': 537, 'x': 334}), (58, 179, 218): Coordinate({'y': 612, 'x': 460}), (131, 84, 50): Coordinate({'y': 643, 'x': 265}), (254, 216, 61): Coordinate({'y': 757, 'x': 427}), (94, 124, 22): Coordinate({'y': 858, 'x': 258}), (128, 199, 31): Coordinate({'y': 913, 'x': 395}), (176, 46, 38): Coordinate({'y': 1011, 'x': 271}), (243, 139, 170): Coordinate({'y': 1044, 'x': 419}), (29, 29, 33): Coordinate({'y': 1129, 'x': 295}), (23, 124, 125): Coordinate({'y': 568, 'x': 805}), (193, 103, 29): Coordinate({'y': 539, 'x': 887}), (156, 65, 149): Coordinate({'y': 636, 'x': 889}), (109, 44, 146): Coordinate({'y': 654, 'x': 789}), (52, 58, 135): Coordinate({'y': 746, 'x': 793}), (50, 141, 171): Coordinate({'y': 720, 'x': 868}), (197, 169, 53): Coordinate({'y': 809, 'x': 841}), (105, 70, 45): Coordinate({'y': 810, 'x': 756}), (103, 156, 31): Coordinate({'y': 894, 'x': 810}), (189, 111, 135): Coordinate({'y': 961, 'x': 748}), (77, 100, 24): Coordinate({'y': 900, 'x': 682}), (139, 41, 36): Coordinate({'y': 995, 'x': 663})}
    # top_left = Coordinate({'y': 251, 'x': 1175})
    # bottom_right = Coordinate({'y': 1020, 'x': 1947})

    delta = bottom_right - top_left

    with Image.open(name) as img:
        img = img.convert("RGB")
        img = img.resize((tall, wide))
        # dummy image to hold palette??
        palimage = Image.new('P', (1, 1))
        # this function for some reason requires the palette to be flattened so fuck off
        flat_pal = []
        for col in list(e_palette.keys())[:256]:
            flat_pal.extend([col.r, col.b, col.g])
        palimage.putpalette(flat_pal)

        img = img.quantize(colors=len(e_palette), palette=palimage)
        img = img.convert("RGB")
        # img.show()
        pixels = img.load()
        for x in range(tall):
            for y in range(wide):
                target_px = pixels[x, y]

                # click on palette
                palette_entry = e_palette[Color(r=target_px[0], g=target_px[1], b=target_px[2])]

                click_color(palette_entry)

                # click on canvas

                pixel_pos = top_left + Coordinate(x=delta.x * (x / 31), y=delta.y * (y / 31))
                muis.position = (pixel_pos.x, pixel_pos.y)
                # time.sleep(1/60)
                muis.click(mouse.Button.left)
                time.sleep(1 / 100)
    time.sleep(1)
    img.show()


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
if input("type `y` to load saved calibration, or anything else to not, then press enter.\n").strip() == "y":
    from savedcalibration import *

main()
