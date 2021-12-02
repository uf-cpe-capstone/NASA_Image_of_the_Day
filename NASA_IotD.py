#!/usr/bin/python
import json, requests
import subprocess as sp
from PIL import Image, ImageDraw, ImageFont

NASA_API_KEY_FILE = "api_key.txt"
NASA_API_URL = "https://api.nasa.gov/planetary/apod?api_key="
with open(NASA_API_KEY_FILE, 'r') as file:
    NASA_API_URL += file.read().strip()
NASA_API_RESPONSE_FILE = "response.json"
NASA_IMAGE_FILE_RAW = "iotd_raw.jpg"
NASA_IMAGE_FILE_PROCESSED = "iotd_processed.jpg"

# these are the keys for the dictionary fields we got from the API
COPYRIGHT_KEY = "copyright"
DATE_KEY   = "date"
TITLE_KEY  = "title"
HD_URL_KEY = "hdurl"
DESC_KEY   = "explanation"

# these are the constants for our display calculations
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080
SCREEN_ASPECT = SCREEN_WIDTH / SCREEN_HEIGHT
MARGIN = 24
IMAGE_WIDTH = SCREEN_WIDTH - 2*MARGIN
IMAGE_HEIGHT = SCREEN_HEIGHT - 2*MARGIN
IMAGE_ASPECT = IMAGE_WIDTH / IMAGE_HEIGHT

def api_request():
    with open(NASA_API_RESPONSE_FILE, 'wb') as file:
        r = requests.get(NASA_API_URL)
        if (r.status_code == 403):
            exit("Error, you need to get a NASA API key!");
            return
        elif (r.status_code != 200):
            exit("Error, " + NASA_API_URL + " returned non-200 response!")
            return
        file.write(r.content)

def fetch_image():
    with open(NASA_API_RESPONSE_FILE, 'r') as file:
        data = json.load(file)
        url  = data[HD_URL_KEY] # for testing: "https://picsum.photos/1200/800" 
    with open(NASA_IMAGE_FILE_RAW, 'wb') as file:
        r = requests.get(url) 
        if (r.status_code != 200):
            exit("Error: " + url + " returned non-200 response!")
            return
        print("Successfully got NASA image of the day.")
        file.write(r.content)

def draw_text():
    with Image.open(NASA_IMAGE_FILE_RAW) as pic:
        # rescale if pic is too big
        if (pic.width > IMAGE_WIDTH or pic.height > IMAGE_HEIGHT):
            pic_aspect = pic.width / pic.height
            rescale = 1
            if (pic_aspect > IMAGE_ASPECT):
                # rescale based on width
                rescale = IMAGE_WIDTH / pic.width
            else:
                rescale = IMAGE_HEIGHT / pic.height
            print("rescale factor: " + str(rescale))
            pic = pic.resize((round(rescale*pic.width), round(rescale*pic.height)))
            print("Rescaled width: " + str(pic.width))
            print("Rescaled height: " + str(pic.height))
        with open(NASA_API_RESPONSE_FILE, 'r') as file:
            # get the data from the json file
            data     = json.load(file)
            title    = data[TITLE_KEY]
            #author   = data[COPYRIGHT_KEY]
            date     = data[DATE_KEY]
            desc_raw = data[DESC_KEY]
            # process the description, adding newlines
            desc_words = desc_raw.split()
            desc_text = ""
            word_count = len(desc_words)
            word_wrap_n = 5
            for word_idx in range(word_count):
                if (word_idx == (word_count - 1)):
                    # put last word with no space if we're at the end
                    desc_text += desc_words[word_idx]
                elif (word_idx % word_wrap_n == 0):
                    # put a line break every <word_wrap_n> words
                    desc_text += desc_words[word_idx] + "\n"
                else:
                    desc_text += desc_words[word_idx] + " "
            # get the items we need to draw the final image
            fnt = ImageFont.truetype("/usr/share/fonts/ubuntu/Ubuntu-R.ttf", 20)
            screen = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT))
            paste_x = round((screen.width - pic.width) / 2)
            paste_y = round((screen.height - pic.height) / 2)
            screen.paste(pic, (paste_x, paste_y))
            screen_draw = ImageDraw.Draw(screen)
            # configure and overlay the text
            text_color = (255, 255, 255)
            desc_xy = (MARGIN, MARGIN)
            desc_anchor = "la"
            desc_align = "left"
            screen_draw.multiline_text(desc_xy, desc_text, font=fnt, fill=text_color, anchor=desc_anchor, align=desc_align)
            title_xy = (screen.width - (MARGIN+1), MARGIN)
            title_anchor = "ra"
            title_align = "right"
            title_text = title + "\n" + date
            screen_draw.multiline_text(title_xy, title_text, font=fnt, fill=text_color, anchor=title_anchor, align=title_align)
        screen.save(NASA_IMAGE_FILE_PROCESSED)

def execute_command():
    print("Killing all running fbi processes...")
    kill_cmd = "killall fbi"
    ret = sp.run(kill_cmd.split(), capture_output=True)
    fbi_cmd = "fbi -T 3 -d /dev/fb0 -nocomments -noverbose " + NASA_IMAGE_FILE_PROCESSED
    ret = sp.run(fbi_cmd.split(), capture_output=True)
    if (ret.returncode != 0):
        exit("Error executing fbi command!")
        return
    print("Successfully executed fbi command.")


api_request()
fetch_image()
draw_text()
execute_command()
