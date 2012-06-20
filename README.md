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
or change the UART you are using. To enable the defaults for example:

    # MUX SETTINGS (Ängström 2012.05 on BeagleBone) 
    echo 1 > /sys/kernel/debug/omap_mux/spi0_sclk
    echo 1 > /sys/kernel/debug/omap_mux/spi0_d0 

UART can be changed by tweaking the serial port value in printer.py.

Thanks to Matt Richardson for the initial pointers on controlling the
device via Python.

Author: Lauri Kainulainen / White Sheep Isobar (whitesheep.fi)


(Licensed under the MIT license)