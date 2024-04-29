from drive import SSD1305

from PIL import Image, ImageDraw, ImageFont
import requests

import datetime
import time
import math
import threading
import json

TIME_FOR_SCREEN = 10
NUMBER_OF_SCREENS = 3

with open("configs.json") as file:
    configs = json.load(file)


def update_temperature():
    global temperature, running
    while running:
        error = False

        try:
            r = requests.get(configs["thermometer_url"])
        except Exception:
            temperature = "-- °C"
            error = True

        if not error:
            if r.status_code == 200:
                rj = r.json()
            else:
                temperature = "-- °C"
                error = True

        if not error:
            if rj["status"] != "ok":
                temperature = "-- °C"
                error = True

        if not error:
            temperature = f'{rj["temperature"]:.1f} °C'

        time.sleep(30)


temperature = "-- °C"

disp = SSD1305.SSD1305()

disp.Init()

disp.clear()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

draw.rectangle((0, 0, width, height), outline=0, fill=0)

padding = 0
top = padding
bottom = height-padding
x = 0

# font = ImageFont.truetype('04B_08__.TTF', 8)
font = ImageFont.truetype('fonts/VCR_OSD_MONO_1.001.ttf', 24)

running = True

threading.Thread(target=update_temperature).start()

start_time = time.time()

while True:
    try:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        screen = math.floor((int(time.time() - start_time) % (TIME_FOR_SCREEN * NUMBER_OF_SCREENS)) / (TIME_FOR_SCREEN))

        if screen == 0:
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            draw.text((10, 7), time_str, font=font, fill=255)
        elif screen == 1:
            date_str = datetime.datetime.now().strftime("%d.%m.%y")
            draw.text((10, 7), date_str, font=font, fill=255)
        elif screen == 2:
            # date_str = datetime.datetime.now().strftime("%d.%m.%y")
            draw.text((20, 7), temperature, font=font, fill=255)

        # draw.text((x, top), time_str, font=font, fill=255)

        disp.getbuffer(image)
        disp.ShowImage()
        time.sleep(.1)
    except (KeyboardInterrupt):
        print("\n")
        running = False
        break
