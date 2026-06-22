# Auto Joy of Painting

a basic pynput/pyautogui Python script to automatically paint dithered pngs into the [Joy of Painting minecraft mod](https://modrinth.com/mod/joy-of-painting/)

this is NOT a Java mod, it just uses direct OS-level "move the mouse and click here" shit to control it. requires some calibration.

# DISCLAIMER

many servers with the JoP mod have programs like this explicitly against the rules. use at your own risk.

# demo

https://github.com/user-attachments/assets/a8c6e498-bb9d-40fd-ba6e-2a63f1fd34e7

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
     - tip: you can use the extra 12 palette slots to add extra colors, just tell the program you have more than 16 colors
- the program will then paint for you :3


# future plans

- currently, the program only paints with the colors you provide it (max 28 cause thats how many fit on a palette) and using dithering math to approximate other colors. i'm convinced it'd be possible, via mixing, to achieve most, if not all, RGB colors, removing dithering artifacts entirely, but idk enough about how the painting mods mixing system works to do this yet

- right now, remembering settings is NOT automatic, though it is possible (by copy pasting the output into variables). need to make this more automatic.
