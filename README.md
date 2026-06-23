# Auto Joy of Painting

a basic pynput/pyautogui Python script to automatically paint dithered pngs into
the [Joy of Painting minecraft mod](https://modrinth.com/mod/joy-of-painting/)

this is NOT a Java mod, it just uses direct OS-level "move the mouse and click here" shit to control it. requires some
calibration.

# DISCLAIMER

many servers with the JoP mod have programs like this explicitly against the rules. use at your own risk.

# demo

https://github.com/user-attachments/assets/650963a6-2ef5-4130-8191-4f78ed62cc04

# setup

- download or clone this repo (unzip if its a zip)
- download and install [uv for python](https://docs.astral.sh/uv/)
- open terminal in the downloaded folder
- in your terminal, run `uv run main.py`

# usage

- keep both minecraft and the terminal window visible on your monitor, youll need to interact with both
- the program will run a few calibration steps
    - the program will ask some questions, follow as it says.
    - it will calibrate the canvas's position by having you click the top-left and bottom-right corners
    - then you tell it the colors you have by clicking the BACKGROUND of every color
        - to ensure proper calibration, it's best to not move the mouse for like half a second between clicks
        - tip: you can use the extra 12 palette slots to add extra colors, just tell the program you have more than 16
          colors
- the program will then paint for you :3

# notes

- the program is currently configured to mix colors up to a depth of 3 (very diminishing returns, 300k color palette)
- mixing direclty on the palette might be possible, and might be MUCH quicker, but id have to look into how *that* math
  works, it seems to work different than canvas opacity
- the "`def delay()`" function is configured by default for 1/60 s between actions, it is possible to increase this to a
  bit less than one action per frame if you have a high refresh rate monitor, thats where it seems to max out