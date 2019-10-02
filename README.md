# TTF2BMH
This repository contains four python scripts to generate monochrome bitmap header fonts with character size of 24 to 64 pixels. 
  
# Release 1.0
The software is released under version 1.0 with the description below. 
An updated version without the external BMFT Software, commandline interface, and more options will be shortly released under version 2.0. 

# Overall functionality
The software renders arbitrary TTF Fonts into a 8-bit depth TGA file, further converts each character to a monochrome array of bytes, and stores these arrays in a C header file. This header file can be used for any C microcontroller Code so that the characters can be displayed on monochrome OLED or LCD Display. 
* ttf2bmh_digit_font.py : Scripts converts digits (0123456789:) from system installed fonts
* ttf2bmh_digit_file.py : Scripts converts digits (0123456789:) from TTF files 
* ttf2bmh_ascii_font.py : Scripts converts ascii characters 32 - 126 from system installed fonts
* ttf2bmh_ascii_file.py : Scripts converts ascii characters 32 - 126  from TTF files 

# Header File description
The header file contains one byte array per selected character, with currently a variable type "static const uint8_t bitmap_32[] PROGMEM", so that it compiles for Microchip AVR microcontrollers. The variable type can be changed in the source code, so that header files for different MCU architectures can be generated. 
The byte array s followed by a adress pointer, so that the characters can be adressed easily. 
The header file also contains the character width W of the each character, so that correct spacing can be calculated and memory can be saved for all zero columns.  
The byte array is ordered the following: 
* Each byte contains 8 bits for one column with 8 pixel-rows. 
* For a character height of 24, three bytes (three byte-rows) are required for a full column
* The first W bytes describe the first byte-row, the second W bytes describe the second byte-row, etc. 

# Usage
### scripts converting system installed fonts 
The scripts can be run either from commandline or from the ipython notebook and must be started from the src directory. 
The desired font names and font sizes need to be selected by changing the python code in the header. 
### scripts converting ttf files
The desired folder path and font sizes can be selected by changing the source code. The script will search for fonts in the subdirectories and convert each file wich each of the selected font sizes. 

The font export definitions are used from the initial bmfc files as shared with the repo. In the files, the actual font size and other settings could be changed to further desired values. 

# Requirements
The program is using and executing the AngelCode bmfont software (uner zlib license), which needs to be downloaded here:   https://www.angelcode.com/products/bmfont/ 

# Examples
The scripts have been used to create the fonts of my BMH_fonts repository https://github.com/jdmorise/BMH-fonts . 

# Disclaimer
The current source code does not follow good coding style and is not readable well. I will work on improvements in the future. 

