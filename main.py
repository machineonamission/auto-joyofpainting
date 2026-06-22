import os
import sys

import pyautogui
import pynput
from pynput import keyboard, mouse
import time
from coordinates import Coordinate
from PIL import Image


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


def color_calibration():
    global colors, col_count
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
        print(f"{col} at {pos}")
        colors[col] = pos
    print(colors)


def startmsg():
    print("Auto \"Joy of Painting\" Script.")
    print("Press any key to start, press q to quit.")
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

def main():

    startmsg()
    canvas_calibration()
    color_calibration()


    #tall = 32
    #wide = 32
    #col_count = 28
    #colors = {(249, 255, 254): Coordinate({'y': 482, 'x': 789}), (71, 79, 82): Coordinate({'y': 349, 'x': 769}), (157, 157, 151): Coordinate({'y': 360, 'x': 606}), (249, 128, 29): Coordinate({'y': 502, 'x': 625}), (199, 78, 189): Coordinate({'y': 544, 'x': 490}), (22, 156, 156): Coordinate({'y': 396, 'x': 487}), (137, 50, 184): Coordinate({'y': 469, 'x': 387}), (60, 68, 170): Coordinate({'y': 537, 'x': 334}), (58, 179, 218): Coordinate({'y': 612, 'x': 460}), (131, 84, 50): Coordinate({'y': 643, 'x': 265}), (254, 216, 61): Coordinate({'y': 757, 'x': 427}), (94, 124, 22): Coordinate({'y': 858, 'x': 258}), (128, 199, 31): Coordinate({'y': 913, 'x': 395}), (176, 46, 38): Coordinate({'y': 1011, 'x': 271}), (243, 139, 170): Coordinate({'y': 1044, 'x': 419}), (29, 29, 33): Coordinate({'y': 1129, 'x': 295}), (23, 124, 125): Coordinate({'y': 568, 'x': 805}), (193, 103, 29): Coordinate({'y': 539, 'x': 887}), (156, 65, 149): Coordinate({'y': 636, 'x': 889}), (109, 44, 146): Coordinate({'y': 654, 'x': 789}), (52, 58, 135): Coordinate({'y': 746, 'x': 793}), (50, 141, 171): Coordinate({'y': 720, 'x': 868}), (197, 169, 53): Coordinate({'y': 809, 'x': 841}), (105, 70, 45): Coordinate({'y': 810, 'x': 756}), (103, 156, 31): Coordinate({'y': 894, 'x': 810}), (189, 111, 135): Coordinate({'y': 961, 'x': 748}), (77, 100, 24): Coordinate({'y': 900, 'x': 682}), (139, 41, 36): Coordinate({'y': 995, 'x': 663})}
    #top_left = Coordinate({'y': 251, 'x': 1175})
    #bottom_right = Coordinate({'y': 1020, 'x': 1947})

    delta = bottom_right - top_left

    muis = pynput.mouse.Controller()
    with Image.open(input("Input the filename of the image:\n").strip()) as img:
        img = img.convert("RGB")
        img = img.resize((tall, wide))
        # dummy image to hold palette??
        palimage = Image.new('P', (1, 1))
        palette = list(colors.keys())
        # this function for some reason requires the palette to be flattened so fuck off list comprehension
        palimage.putpalette([item for sublist in palette for item in sublist])
        img = img.quantize(colors=col_count, palette=palimage)
        img = img.convert("RGB")
        # img.show()
        pixels = img.load()
        for x in range(tall):
            for y in range(wide):
                target_px = pixels[x, y]

                # click on palette
                palette_coord = colors[target_px]
                muis.position = (palette_coord.x, palette_coord.y)
                # time.sleep(1/60)
                muis.click(mouse.Button.left)
                time.sleep(1/100)

                # click on canvas

                pixel_pos = top_left + Coordinate(x=delta.x * (x / 31), y=delta.y * (y / 31))
                muis.position = (pixel_pos.x, pixel_pos.y)
                # time.sleep(1/60)
                muis.click(mouse.Button.left)
                time.sleep(1/100)
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

main()
