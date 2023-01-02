# TTF2BMH

A conversion tool for Truetype Fonts to bitmap C header files for any character and for use with monochrome LCD or OLED displays  

## Overall functionality
The software renders arbitrary TTF Fonts of character to a monochrome array of bytes, and stores these arrays in a C header file. This file can be used for any C microcontroller Code so that the characters can be displayed on monochrome OLED or LCD Display. A png picture with the rendered characters is also stored within the library.

## Header File description
The header file contains one byte array per selected character, with currently a variable type "const char bitmap_32[]", so that it compiles for Microchip AVR microcontrollers. The variable name is always bitmap_XX, where XX is the decimal ASCII value of that character. The variable type can be changed in the source code, so that header files for different MCU architectures can be generated.
The byte array is followed by an address pointer, so that the characters can be addressed easily.  
The byte array is ordered the following:
* Each byte contains 8 bits for one column with 8 pixel-rows.
* For a character height of 24, three bytes (three byte-rows) are required for a full column
* The first W bytes describe the first byte-row, the second W bytes describe the second byte-row, etc.

## Usage
The script offers a command line interface with somehow self-describing arguments. On the command line, the search path and the folder name can be chosen. Default search path is the Windows Font directory under C:\Windows\Fonts\.


    usage: ttf2bmh.py [-h] [-l] [-f TTF_FOLDER] [-o OUTPUT_FOLDER] [-c CHARACTER_FILENAME] [-C CHARACTERS] [-r RANGE] [--ascii]
                      [--lowerascii] [--font FONT] [-s [FONTSIZE ...]] [-O OFFSET] [--variable_width] [-fh [FONT_HEIGHT ...]]
                      [-a {ascender,top,middle,baseline,bottom,descender}] [-y Y_OFFSET] [--square] [-w WIDTH] [--progmem] [-T] [-p] [-R]

    options:
      -h, --help            show this help message and exit
      -l, --license         show license terms
      -f TTF_FOLDER, --ttf_folder TTF_FOLDER
                            Folder where ttf files are stored (Defaults to C:\Windows\Fonts\ on Windows, /usr/share/fonts on Linux)
      -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                            Folder where bitmapheader output files will be stored. A subfolder for each Font will be created under the
                            directory (Defaults to ./bmhfonts)
      -c CHARACTER_FILENAME, --character_filename CHARACTER_FILENAME
                            filename for characters to be processed
      -C CHARACTERS, --characters CHARACTERS
                            String of characters to be processed (if no character_filename passed in)
      -r RANGE, --range RANGE
                            range of characters, by decimal value in the ASCII table. Example: "32-126" or "96". (overrides -c and -C)
      --ascii               Convert for all ascii characters. Shortcut for "-r 32-126".
      --lowerascii          Convert for all lower ascii characters (punctuation and digits only) Shortcut for "-r 32-64".
      --font FONT           Define Font Name to be processed. Name should include modifier like Bold or Italic. If none is given, all fonts
                            in folder will be processed.
      -s [FONTSIZE ...], --fontsize [FONTSIZE ...]
                            Fontsize (Fontheight) in pixels. Multiple values allowed. Default: 32
      -O OFFSET, --offset OFFSET
                            Y Offset for characters (Default is based off font size)
      --variable_width      Variable width of characters (overrides --square and --width).
      -fh [FONT_HEIGHT ...], --font_height [FONT_HEIGHT ...]
                            Define fontsize of rendered font within the defined pixel image boundary. If defined must have same number of
                            arguments as fontsize.
      -a {ascender,top,middle,baseline,bottom,descender}, --anchor {ascender,top,middle,baseline,bottom,descender}
                            Vertical anchor for the text. For anything but the default (ascender), you will want to adapt Offset.
      -y Y_OFFSET, --y_offset Y_OFFSET
                            Define starting offset of character. Only meaningful if specific fontsize is rendered.
      --square              Make the font square instead of height by (height * 0.75)
      -w WIDTH, --width WIDTH
                            Fixed font width in pixels. Default: height * 0.75 (overrides --square)
      --progmem             C Variable declaration adds PROGMEM to character arrays. Useful to store the characters in porgram memory for AVR
                            Microcontrollers with limited Flash or EEprom
      -T, --Tiny4kOLED      Make C code formatted for Tiny4kOLED. Must be used with --range. (supports both fixed and variable width)
      -p, --print_ascii     Print each character as ASCII Art on commandline, for debugging. Also makes the .h file more verbose.
      -R, --rotate          Rotates the Bitmap to read pixels from left to right then from top to bottom.

The program can also be run directly on Linux systems by doing `./ttf2bmh.py`

## Examples

Conversion of all digits including colon from Font "Courier New", pixel size 32 with variable width.

    $ python ./ttf2bmh.py -s 32 -c ../characters_digits.txt --progmem --font "Courier New" --variable_width
    Converting characters: "0123456789:"
    Courier New_32.h written
    TTF2BMH Finished


Example to convert all fonts in specific folder:

    python ./ttf2bmh.py -s 32 -c ../characters_digits.txt --progmem -f ../ttf_fonts/liberation-fonts-ttf/ --variable_width


Example to convert all system fonts for all ascii values at a size of 32 to a folder `bmh_fonts` in the current directory

    python ./ttf2bmh.py --ascii

Further examples can be found within the ipython notebook RUN within the src folder.
The scripts have been used to create the fonts of my BMH_fonts repository https://github.com/jdmorise/BMH-fonts.

## Requirements
* Python 3
* PIL
* fontTools
* argparse

## Disclaimer
The latest version is not tested on MCU device level yet.
