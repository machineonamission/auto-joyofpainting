# Auto Joy of Painting

a basic pynput/pyautogui Python script to automatically paint dithered pngs into
the [Joy of Painting minecraft mod](https://modrinth.com/mod/joy-of-painting/)

this is NOT a Java mod, it just uses direct OS-level "move the mouse and click here" shit to control it. requires some
calibration.

# DISCLAIMER

many servers with the JoP mod have programs like this explicitly against the rules. use at your own risk.

# demo

<img width="1407" height="1630" alt="image" src="https://github.com/user-attachments/assets/f2032277-581c-4be9-a3d1-496c72726a43" />

https://github.com/user-attachments/assets/2686d1cb-111b-45f6-8439-c50c6b911f8e


# setup

- download or clone this repo (unzip if its a zip)
- download and install [uv for python](https://docs.astral.sh/uv/)
- open terminal in the downloaded folder
- in your terminal, run `uv run main.py`

# usage

- keep both minecraft and the terminal window visible on your monitor, youll need to interact with both
- the program will run a few calibration steps
    - the program will ask some questions, follow as it says.
    - it will calibrate the position of the onscreen elements (colors, ui elements, etc) by having you click on them
    - it will then run some math to figure out how to mix colors for the image
- the program will then paint for you :3

# notes

- the "`def delay()`" function is configured by default for 1/60 s between actions, it is possible to increase this to a
  bit less than one action per frame if you have a high refresh rate monitor, thats where it seems to max out
