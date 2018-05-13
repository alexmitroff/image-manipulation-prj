# image-manipulation-prj
convert image to rect svg

## Quick mac os setup
* Install python >= 3.6 [like this one](https://www.python.org/ftp/python/3.6.5/python-3.6.5-macosx10.6.pkg)
* Open **terminal**
* `pip3 install pillow`
* `pip3 install svgwrite`

## Usage
* [Download project](https://github.com/alexmitroff/image-manipulation-prj/archive/master.zip)
* unzip project, for example to **Desktop** directory
* `python3 ~/Desktop/image.py -i path_to_image/image.jpg -s 128 -c 8`

### Flags
* **-i** -- path to image
* **-s** -- dots per line in resulting svg image
* **-c** -- the number of colors in resulting svg image
