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


def main():
    # print("Auto \"Joy of Painting\" Script.")
    # print("Press any key to start, press q to quit.")
    # wait_for_key()
    # print("Canvas calibration:")
    # print("Click the top left corner.")
    # top_left = click_pos()
    # print(top_left)
    # print("Click the bottom right corner.")
    # bottom_right = click_pos()
    # print(bottom_right)
    # tall = intput("How many pixels TALL is your canvas? (small is 16, large is 32)", 32)
    # wide = intput("How many pixels WIDE is your canvas? (small is 16, large is 32)", 32)
    # print(f"{tall}x{wide} canvas")
    #
    print("Color calibration:")
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

    # while True:
    #     pos = pyautogui.position()
    #     col = pyautogui.pixel(pos.x, pos.y)
    #     print(col)

    tall = 32
    wide = 32
    col_count = 16
    # colors = {(131, 84, 50): Coordinate({'y': 734, 'x': 428}), (249, 255, 254): Coordinate({'y': 329, 'x': 789}), (71, 79, 82): Coordinate({'y': 362, 'x': 627}), (228, 117, 27): Coordinate({'y': 497, 'x': 632}), (249, 128, 29): Coordinate({'y': 394, 'x': 483}), (22, 156, 156): Coordinate({'y': 464, 'x': 504}), (199, 78, 189): Coordinate({'y': 471, 'x': 384}), (137, 50, 184): Coordinate({'y': 575, 'x': 429}), (58, 179, 218): Coordinate({'y': 512, 'x': 306}), (254, 216, 61): Coordinate({'y': 860, 'x': 272}), (94, 124, 22): Coordinate({'y': 911, 'x': 381}), (128, 199, 31): Coordinate({'y': 974, 'x': 309}), (176, 46, 38): Coordinate({'y': 1040, 'x': 378}), (25, 25, 28): Coordinate({'y': 1133, 'x': 300})}

    top_left = Coordinate({'y': 251, 'x': 1175})
    bottom_right = Coordinate({'y': 1020, 'x': 1947})

    delta = bottom_right - top_left

    muis = pynput.mouse.Controller()
    with Image.open("input.jpg") as img:
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
                time.sleep(1/60)
                muis.click(mouse.Button.left)
                time.sleep(1/60)

                # click on canvas

                pixel_pos = top_left + Coordinate(x=delta.x * (x / 31), y=delta.y * (y / 31))
                muis.position = (pixel_pos.x, pixel_pos.y)
                time.sleep(1/60)
                muis.click(mouse.Button.left)
                time.sleep(1/60)
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
