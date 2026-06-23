import math
import os
import time
from collections import defaultdict

import pyautogui
import pynput
import tqdm.contrib.itertools
from PIL import Image
from pynput import keyboard, mouse

import quantizer
from common import *

# from colour import Color

muis = pynput.mouse.Controller()


def delay():
    # NOTE: THIS SEEMS TO BE MAXED AT 1 / FPS OR IT MISSES INPUTS!
    time.sleep(1 / 60)


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


def print_and_return(e):
    print(e)
    return e


def click_pos():
    e = wait_for_click()
    return print_and_return(Coordinate(x=e.x, y=e.y))


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
    print("Click to the game, then press any key (except q) to begin.")
    wait_for_key()


def canvas_calibration():
    global top_left, bottom_right, tall, wide, delta
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
    delta = bottom_right - top_left


def color_calibration():
    global colors, col_count, palette
    print("Color calibration: ")
    colors = OrderedDict()
    positions = []
    col_count = intput("How many colors does your palette have? (default 16)", 16)
    for i in range(col_count):
        print(f"Color {i + 1}/{col_count}:")
        print("Click a new color on the palette")
        positions.append(click_pos())
    # wait_for_unclick()
    # muis.position = (pos.x + 500, pos.y)
    # print(pos)
    # time.sleep(0.5)
    # muis.position = (pos.x + 500, pos.y)
    # col = pyautogui.pixel(pos.x, pos.y)
    # col = Color(r=col[0], g=col[1], b=col[2])
    # muis.position = (pos.x, pos.y)
    #
    # print(f"{col} at {pos}")
    # colors[col] = pos
    # positions = [Coordinate({'y': 156, 'x': 1803}), Coordinate({'y': 217, 'x': 1812}),
    #              Coordinate({'y': 211, 'x': 1743}),
    #              Coordinate({'y': 157, 'x': 1742}), Coordinate({'y': 168, 'x': 1694}),
    #              Coordinate({'y': 232, 'x': 1698}),
    #              Coordinate({'y': 205, 'x': 1642}), Coordinate({'y': 254, 'x': 1612}),
    #              Coordinate({'y': 286, 'x': 1673}),
    #              Coordinate({'y': 305, 'x': 1593}), Coordinate({'y': 327, 'x': 1651}),
    #              Coordinate({'y': 361, 'x': 1599}),
    #              Coordinate({'y': 381, 'x': 1652}), Coordinate({'y': 414, 'x': 1605}),
    #              Coordinate({'y': 437, 'x': 1653}),
    #              Coordinate({'y': 476, 'x': 1615})]
    print(positions)
    print("determining color RGB...")
    click(opacities[1.0])
    for color_pos in positions:
        click(color_pos)
        click(bottom_right)
        move_to(color_pos)
        time.sleep(0.5)
        col = pyautogui.pixel(bottom_right.x, bottom_right.y)
        col = Color(r=col[0], g=col[1], b=col[2])

        print(f"{col} at {color_pos}")
        colors[col] = color_pos

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
    for opacity in [1.0, 0.75, 0.5, 0.25]:
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
    print("pre-computing color mixing")
    e_palette = OrderedDict()
    for color, pos in colors.items():
        e_palette[color] = JoPPureColor(color=color, position=pos)

    first_e_palette = list(e_palette.values()).copy()

    for depth in range(3):
        for (mixcol, palcol, opacity) in tqdm.contrib.itertools.product(list(e_palette.values()).copy(),
                                                                        first_e_palette, [0.5, 0.75],
                                                                        desc=f"searching depth {depth}"):
            new_col = mix(palcol.color, mixcol.color, opacity)
            if new_col not in e_palette:
                e_palette[new_col] = JoPMixedColor(color=new_col, color1=palcol,
                                                   color2=mixcol, opacity=opacity)
    print(f"{len(e_palette)} colors found")


def save_calibration():
    print("saving...")
    with open("savedcalibration.py", "w+") as f:
        f.write("from collections import OrderedDict\nfrom common import *\n\n")
        for var in ["tall", "wide", "top_left", "bottom_right", "col_count", "colors", "opacities", "mixer",
                    "mix_slot", "water_slot", "delta"]:
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


def move_to(c: Coordinate):
    muis.position = (c.x, c.y)


def drag_between(frm: Coordinate, to: Coordinate):
    move_to(frm)
    delay()
    muis.press(mouse.Button.left)
    delay()
    move_to(to)
    delay()
    muis.release(mouse.Button.left)
    delay()


def click_color(color: JoPColor, change_opacity=True):
    if isinstance(color, JoPPureColor):
        if change_opacity:
            set_opacity(1.0)
        click(color.position)
    elif isinstance(color, JoPMixedColor):
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


def get_color(target_px: tuple[int, int, int]):
    # off-by-one hack to confirm
    for r_offset in [0, -1, 1, -2, 2]:
        for g_offset in [0, -1, 1, -2, 2]:
            for b_offset in [0, -1, 1, -2, 2]:
                try:
                    col = Color(r=int(target_px[0]), g=int(target_px[1]), b=int(target_px[2]))
                    offset = Color(r=r_offset, g=g_offset, b=b_offset)
                    col += offset
                    # click on palette
                    palette_entry = e_palette[col]
                    # print(col, offset)
                    return palette_entry
                except KeyError:
                    pass
    # print(target_px)
    raise KeyError


def main():
    print("Auto \"Joy of Painting\" Script by Machine on a Mission.\nPress q to quit.")

    did_calibration = False
    did_key = False

    if not all_defined("tall", "wide", "top_left", "bottom_right", "delta"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        canvas_calibration()
        did_calibration = True

    if not all_defined("opacities", "mixer", "mix_slot", "water_slot"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        mix_calibration()
        did_calibration = True

    if not all_defined("col_count", "colors"):
        if not did_calibration and not did_key:
            startmsg()
            did_key = True
        color_calibration()
        did_calibration = True

    name = input("Input the filename of the image:\n").strip()
    # name = "monalisa.jpg"

    if did_calibration and input(
            "type `y` to save calibration, or anything else to not, then press enter.\n").strip() == "y":
        save_calibration()

    canvas_w = intput("How many canvases wide?", 1)
    canvas_h = intput("How many canvases tall?", 1)
    print(f"{canvas_w * canvas_h} canvases")

    mix_calculation()

    # tall = 32
    # wide = 32
    # col_count = 28
    # colors = {(249, 255, 254): Coordinate({'y': 482, 'x': 789}), (71, 79, 82): Coordinate({'y': 349, 'x': 769}), (157, 157, 151): Coordinate({'y': 360, 'x': 606}), (249, 128, 29): Coordinate({'y': 502, 'x': 625}), (199, 78, 189): Coordinate({'y': 544, 'x': 490}), (22, 156, 156): Coordinate({'y': 396, 'x': 487}), (137, 50, 184): Coordinate({'y': 469, 'x': 387}), (60, 68, 170): Coordinate({'y': 537, 'x': 334}), (58, 179, 218): Coordinate({'y': 612, 'x': 460}), (131, 84, 50): Coordinate({'y': 643, 'x': 265}), (254, 216, 61): Coordinate({'y': 757, 'x': 427}), (94, 124, 22): Coordinate({'y': 858, 'x': 258}), (128, 199, 31): Coordinate({'y': 913, 'x': 395}), (176, 46, 38): Coordinate({'y': 1011, 'x': 271}), (243, 139, 170): Coordinate({'y': 1044, 'x': 419}), (29, 29, 33): Coordinate({'y': 1129, 'x': 295}), (23, 124, 125): Coordinate({'y': 568, 'x': 805}), (193, 103, 29): Coordinate({'y': 539, 'x': 887}), (156, 65, 149): Coordinate({'y': 636, 'x': 889}), (109, 44, 146): Coordinate({'y': 654, 'x': 789}), (52, 58, 135): Coordinate({'y': 746, 'x': 793}), (50, 141, 171): Coordinate({'y': 720, 'x': 868}), (197, 169, 53): Coordinate({'y': 809, 'x': 841}), (105, 70, 45): Coordinate({'y': 810, 'x': 756}), (103, 156, 31): Coordinate({'y': 894, 'x': 810}), (189, 111, 135): Coordinate({'y': 961, 'x': 748}), (77, 100, 24): Coordinate({'y': 900, 'x': 682}), (139, 41, 36): Coordinate({'y': 995, 'x': 663})}
    # top_left = Coordinate({'y': 251, 'x': 1175})
    # bottom_right = Coordinate({'y': 1020, 'x': 1947})

    print("loading and prepping image...")
    with Image.open(name) as img:
        img = img.convert("RGB")
        img = img.resize((wide * canvas_w, tall * canvas_h))

        # Force the output type to truecolor (RGB) to drop alpha or indexing
        # img.type = 'truecolor'
        # img.save(filename="PNG24:out.png")
        # img = img.convert("RGB")
        print("quantizing...")
        quantized = quantizer.quantize(img, e_palette)
        c_count = 0
        for canvas_wi in range(canvas_w):
            for canvas_hi in range(canvas_h):
                c_count += 1
                print(f"canvas at ({canvas_wi}, {canvas_hi}) ({c_count} / {canvas_w * canvas_h})")
                input(f"press enter on the console when ready (canvas open)")
                startmsg()
                yrange = range(canvas_hi * tall, (canvas_hi * tall) + tall)
                xrange = range(canvas_wi * wide, (canvas_wi * wide) + wide)
                # crop.show()
                # nonsense color so it always works
                all_color_pixels = defaultdict(list)
                for y in yrange:
                    for x in xrange:
                        px = quantized[y][x]
                        all_color_pixels[px.color].append((x, y))
                # last_col = Color(r=256, g=256, b=256)

                # since we use the last pixel for mixing, always do it last
                x = xrange[-1]
                y = yrange[-1]
                px = quantized[y][x]
                last_pixel = all_color_pixels.pop(px.color)

                allcolors = [*all_color_pixels.items(), (px.color, last_pixel)]

                for color, coords in tqdm.tqdm(allcolors, desc="Painting"):
                    # print(color,coords)
                    # print(x,y)/
                    # target_px = pixels[x, y]

                    # col = Color(r=target_px[0], g=target_px[1], b=target_px[2])
                    # click on palette
                    # palette_entry = quantized[y][x]
                    # col = palette_entry.color
                    # if last_col != col:
                    click_color(e_palette[color])
                    # last_col = col

                    # click on canvas
                    for (x, y) in coords:
                        pixel_pos = top_left + Coordinate(x=delta.x * (x / 31), y=delta.y * (y / 31))
                        click(pixel_pos)

                # pbar.update(1)

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

# i fucking love storing python data as py files lmao
if input("type `y` to load saved calibration, or anything else to not, then press enter.\n").strip() == "y":
    from savedcalibration import *

main()
