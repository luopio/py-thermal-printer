#coding=utf-8
import serial, time

#================================================#
#================================================#
# MUX SETTINGS (Ängström 2012.05)
# echo 1 > /sys/kernel/debug/omap_mux/spi0_sclk
# echo 1 > /sys/kernel/debug/omap_mux/spi0_d0 
#================================================#
#================================================#

    
class ThermalPrinter(object):
    ''' 
        
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

        @author: Lauri Kainulainen / White Sheep Isobar (whitesheep.fi)

    '''

    BAUDRATE = 19200
    TIMEOUT = 3
    SERIALPORT = '/dev/ttyO2'
    # pixels with more color value (average for multiple channels) are counted as white
    black_threshold = 20
    # pixels with less alpha than this are counted as white
    alpha_threshold = 127
    # Set "max heating dots", "heating time", "heating interval"
    # n1 = 0-255 Max printing dots, Unit (8dots), Default: 7 (64 dots)
    # n2 = 3-255 Heating time, Unit (10us), Default: 80 (800us)
    # n3 = 0-255 Heating interval, Unit (10us), Default: 2 (20us)
    # The more max heating dots, the more peak current will cost
    # when printing, the faster printing speed. The max heating
    # dots is 8*(n1+1). The more heating time, the more density,
    # but the slower printing speed. If heating time is too short,
    # blank page may occur. The more heating interval, the more
    # clear, but the slower printing speed.
    heatingDots = 80
    heatTime = 255
    heatInterval = 250

    printer = None
    
    def __init__(self):
        self.printer = serial.Serial(self.SERIALPORT, self.BAUDRATE, timeout=self.TIMEOUT)
        self.printer.write(chr(27)) # ESC - command
        self.printer.write(chr(55)) # 7   - print settings
        self.printer.write(chr(self.heatingDots))  # Heating dots (20=balance of darkness vs no jams) default = 20
        self.printer.write(chr(self.heatTime)) # heatTime Library default = 255 (max)
        self.printer.write(chr(self.heatInterval)) # Heat interval (500 uS = slower, but darker) default = 250

        # Description of print density from page 23 of the manual:
        # DC2 # n Set printing density
        # Decimal: 18 35 n
        # D4..D0 of n is used to set the printing density. Density is
        # 50% + 5% * n(D4-D0) printing density.
        # D7..D5 of n is used to set the printing break time. Break time
        # is n(D7-D5)*250us.
        # (Unsure of the default value for either -- not documented)
        printDensity = 14 # 120% (? can go higher, text is darker but fuzzy)
        printBreakTime = 4 # 500 uS
        self.printer.write(chr(18))
        self.printer.write(chr(35))
        self.printer.write(chr((printBreakTime << 5) | printDensity))


    def print_text(self, msg, chars_per_line=None):
        ''' Print some text defined by msg. If chars_per_line is defined, 
            inserts newlines after the given amount. Use normal '\n' line breaks for 
            empty lines. '''
        if chars_per_line == None:
            self.printer.write(msg)
        else:
            l = list(msg)
            le = len(msg)
            for i in xrange(chars_per_line + 1, le, chars_per_line + 1):
                l.insert(i, '\n')
            self.printer.write("".join(l))
            print "".join(l)
        

    def print_bitmap(self, pixels, w, h, output_png=False):
        ''' 
            Props for Adafruit as this code has been mostly ported from their Arduino
            library. 
            - takes a pixel array. RGBA, RGB, or one channel plain list of values (ranging from 0-255).
            - w = width of image, h = height of image
            - if "output_png" is set, prints an "print_bitmap_output.png" in the same folder using the same
            thresholds as the actual printing commands. Useful for seeing if there are problems with the 
            original image (this requires PIL).

            Example code with PIL:
                import Image, ImageDraw
                i = Image.open("lammas_grayscale-bw.png")
                data = list(i.getdata())
                w, h = i.size
                p.print_bitmap(data, w, h)
        '''
        counter = 0
        if output_png:
            test_img = Image.new('RGB', (384, h))
            draw = ImageDraw.Draw(test_img)

        self.printer.write(chr(10)) # Paper feed
        
        for rowStart in xrange(0, h, 256):
            chunkHeight = 255 if (h - rowStart) > 255 else h - rowStart            
            time.sleep(0.5)
            self.printer.write(chr(18))
            self.printer.write(chr(42))
            self.printer.write(chr(chunkHeight))
            self.printer.write(chr(w / 8))
            time.sleep(0.5)
                        
            for i in xrange(0, (w / 8) * chunkHeight, 1):
                # read one byte in
                byt = 0
                for xx in xrange(8):
                    pixel_values = pixels[counter]
                    counter += 1
                    # check if this is black or white
                    # for RGBA
                    if type(pixel_values) == list and len(pixel_values) > 3 and \
                       pixel_values[3] > self.alpha_threshold and sum(pixel_values[0:2]) / 3.0 < self.black_threshold:
                        byt += 1 << (7 - xx)
                        if output_png: draw.point((counter % w, round(counter / w)), fill=(0, 0, 0))
                    # for RGB
                    elif type(pixel_values) == list and len(pixel_values) == 3 and sum(pixel_values[0:2]) / 3.0 < self.black_threshold:
                        byt += 1 << (7 - xx)
                        if output_png: draw.point((counter % w, round(counter / w)), fill=(0, 0, 0))
                    # for one channel plain list
                    elif type(pixel_values) == int and pixel_values < self.black_threshold:
                        byt += 1 << (7 - xx)
                        if output_png: draw.point((counter % w, round(counter / w)), fill=(0, 0, 0))
                    # nope, it's white
                    else:
                        if output_png: draw.point((counter % w, round(counter / w)), fill=(255, 255, 255))    
                
                self.printer.write(chr(byt))
            time.sleep(0.5) 
        
        self.printer.write(chr(10)) # Paper feed
        self.printer.write(chr(10)) # Paper feed

        if output_png:
            test_print = open('print-output.png', 'wb')
            test_img.save(test_print, 'PNG')
            test_print.close()


if __name__ == '__main__':
    print "Testing printer"
    p = ThermalPrinter()
    p.print_text("\nHello maailma. How's it going?\n")
    # dependency on Python Imaging Library
    import Image, ImageDraw
    i = Image.open("example-lammas.png")
    data = list(i.getdata())
    w, h = i.size
    p.print_bitmap(data, w, h)
