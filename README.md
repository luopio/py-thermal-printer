Python Thermal Printer Library
==============================

Thermal printing library that controls the "micro panel thermal printer" sold in
shops like Adafruit and Sparkfun (e.g. http://www.adafruit.com/products/597). 
Mostly ported from Ladyada's Arduino library 
(https://github.com/adafruit/Adafruit-Thermal-Printer-Library) to run on
BeagleBone.

Currently handles printing image data and text, but the rest of the
built-in functionality like underlining and barcodes are trivial
to port to Python when needed.

If on BeagleBone or similar device, remember to set the mux settings
or change the UART you are using. See the beginning of this file for
default setup.

Thanks to Matt Richardson for the initial pointers on controlling the
device via Python.

Licensed under the MIT License.

Author: Lauri Kainulainen / White Sheep Isobar (whitesheep.fi)
