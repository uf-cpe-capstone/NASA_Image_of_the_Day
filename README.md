NASA Image of the Day Viewer
============================

This Python script queries the NASA API to recieve a json response containing the URL, description, title, and other attributes for the image of the day.

You will need to obtain a [NASA API key](https://api.nasa.gov:443) and store it in `api_key.txt`. This file is ignored by git.

Using the PIL library, the script scales the image, overlays text on top of it, and displays it.

This script is designed to work without an X server by using the `/dev/fb*` framebuffer device.

### Dependencies

`fbi`, the Linux framebuffer image viewer
Python modules `subprocess`, `PIL`, `json`, and `requests` 
