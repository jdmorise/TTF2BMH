#!/usr/bin/env python
#-------------------------------------------------------------------------
#
#
#    TTF Font to C bitmap header file converter for dot based displays
#    Copyright(c) 2019 JD Morise, jdmorise@yahoo.com
#
#
#-------------------------------------------------------------------------
#
#    (C) 2019, jdmorise@yahoo.com
#
#    This software is part of the TTF2BMH software package to generate bitmap
#    header files for usage of simple OLED or LCD displays with microprocessors
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
#-------------------------------------------------------------------------

import re
import os
import sys
import subprocess
from shutil import copyfile
from fontTools import ttLib
from PIL import Image, ImageFont, ImageDraw
import argparse

VERSION = '2.3'

# Tab to iterate over Font Files in specific directory
def main():
    TTF_FILES = []

    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--license',help='show license terms', action='store_true')
    parser.add_argument('-f','--ttf_folder', default = 'C:\\Windows\\Fonts\\', help='Folder where ttf files are stored (Defaults to C:\\Windows\\Fonts\\ on Windows, /usr/share/fonts on Linux)')
    parser.add_argument('-o','--output_folder', default = 'bmh_fonts', help='Folder where bitmapheader output files will be stored. A subfolder for each Font will be created under the directory (Defaults to ./bmhfonts)')
    parser.add_argument('-c','--character_filename', help='filename for characters to be processed')
    parser.add_argument('-C','--characters', type=str, help='String of characters to be processed (if no character_filename passed in)')
    parser.add_argument('--ascii', action='store_true', help='Convert for all ascii characters (overrides -c and -C)')
    parser.add_argument('--lowerascii', action='store_true', help='Convert for all lower ascii characters (punctuation and digits only) (overrides -c and -C amd --ascii)')
    parser.add_argument('--font', default = '', help='Define Font Name to be processed. Name should include modifier like Bold or Italic. If none is given, all fonts in folder will be processed.')
    parser.add_argument('-s','--fontsize', default='32', choices=['8','16','24', '32', '40', '48', '56', '64', 'all'], help='Fontsize (Fontheight) in pixels. Default: 32')
    parser.add_argument('-O','--offset', type=int, help='Y Offset for characters (Default is based off font size)')
    parser.add_argument('--variable_width', default=False, action='store_true', help='Variable width of characters (overrides --square and --width).')
    parser.add_argument('-fh','--font_height', help='Define fontsize of rendered font within the defined pixel image boundary')
    parser.add_argument('-y','--y_offset', help='Define starting offset of character. Only meaningful if specific fontsize is rendered.')
    parser.add_argument('--progmem',dest='progmem', default=False, action='store_true',help='C Variable declaration adds PROGMEM to character arrays. Useful to store the characters in porgram memory for AVR Microcontrollers with limited Flash or EEprom')
    parser.add_argument('-p','--print_ascii',dest='print_ascii', default=False, action='store_true',help='Print each character as ASCII Art on commandline, for debugging. Also makes the .h file more verbose.')
    parser.add_argument('--square', default=False, action='store_true',help='Make the font square instead of height by (height * 0.75)')
    parser.add_argument('-w','--width',help='Fixed font width in pixels. Default: height * 0.75 (overrides --square)')
    parser.add_argument('-a','--anchor', default='ascender', choices=['ascender','top','middle','baseline','bottom','descender'],help='Vertical anchor for the text. For anything but the default (ascender), you will want to adapt Offset.')
    
    args = parser.parse_args()
    
    if sys.platform == 'linux' and args.ttf_folder == "C:\\Windows\\Fonts\\":
        args.ttf_folder = "/usr/share/fonts"

    if len(sys.argv) == 1:
        parser.print_help()
        return(1)
    elif (args.license):
        print_license()
        return(0)
    else :
        progmem = args.progmem
        print_ascii = args.print_ascii
        # Folder to iterate on
        ttf_searchfolder = args.ttf_folder
        output_folder = args.output_folder

        if not (os.path.exists(output_folder)):
            os.mkdir(output_folder)

        if not (os.path.exists(ttf_searchfolder)):
            print('TTF Folder does not exist')
            return(-1)

        variable_width = args.variable_width

        Target_Font = args.font
        if not (Target_Font == ''):
            ttf_filename, ttf_abs_dir = get_ttf_filename (Target_Font, ttf_searchfolder)
            if(ttf_filename == -1):
                print('No font with name: ' + Target_Font +' found' )
                return(-1)
            else:
                ttf_file = {'dir': ttf_abs_dir, 'filename': ttf_filename}
            TTF_FILES.append(ttf_file)
        else:
            TTF_FILES = search_ttf_folder(ttf_searchfolder)


        # Definition of Font Heights and offsets
        font_heights = [8, 16, 24, 32, 40, 48, 56, 64]
        font_yoffsets = [0, 3, 6, 5, 7, 8, 9, 10]

        if(args.fontsize == 'all'):
            height_indices = range(len(font_heights))
        else:
            height_indices = [font_heights.index(int(args.fontsize))]

        if args.ascii:
            chars = []
            character_line = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
            [chars.append(x) for x in character_line if x not in chars]
            character_line = "".join(chars)
        elif args.lowerascii:
            chars = []
            character_line = " !\"#$%&'()*+,-./0123456789:;<=>?@"
            [chars.append(x) for x in character_line if x not in chars]
            character_line = "".join(chars)            
        elif args.character_filename is not None:
            # Read characters from file
            [character_line,chars] = read_character_file(args.character_filename)
        elif args.characters is not None:
            # Read characters from command line
            chars = []
            character_line = args.characters
            [chars.append(x) for x in character_line if x not in chars]
            character_line = "".join(chars)
        else:
            # Defaults to all numbers + some other small stuff if no chars given
            chars = []
            character_line = "0123456789:"
            [chars.append(x) for x in character_line if x not in chars]
            character_line = "".join(chars)    
            
        print("Converting characters: \"" + character_line + "\"")

        anchor = 'la'
        if args.anchor == 'ascender':
            anchor = 'la'
        elif args.anchor == 'top':
            anchor = 'lt'
        elif args.anchor == 'middle':
            anchor = 'lm'
        elif args.anchor == 'baseline':
            anchor = 'ls'
        elif args.anchor == 'bottom':
            anchor = 'lb'
        elif args.anchor == 'descender':
            anchor = 'ld'

        # Start logging
        logfile = logfile_open(output_folder)

        # Main Loop
        for ttf_file in TTF_FILES:
            # Generate and check file paths and
            ttf_filename = ttf_file['filename']
            ttf_filepath = os.path.abspath(ttf_file['dir'])
            ttf_absolute_filename = os.path.join(ttf_filepath, ttf_filename)
            tt = ttLib.TTFont(ttf_absolute_filename)
            fm = tt['name'].names[4].string
            try:
                Font = fm.decode('utf-8')
            except Exception as ex:
                print(f"Exception: {ex} when reading font file {ttf_absolute_filename}. Skipping.")
                continue                
            
            Font = re.sub('\x00','',Font)

            output_bmh_folder = os.path.join(output_folder, Font)
            if not (os.path.exists(output_bmh_folder)):
                os.mkdir(output_bmh_folder)

            for height_idx in height_indices:
                width_array = []

                # initialize PIL Image
                height = font_heights[height_idx]
                if args.width:
                    width = int(args.width)
                elif args.square:
                    width = height
                else:
                    width = int(height * 0.75)
                if args.offset is not None:
                    yoffset = args.offset
                else:
                    yoffset = font_yoffsets[height_idx]

                # Filename Definitions
                filename = Font + '_' + str(height) # General Filename
                h_filename = os.path.join(output_bmh_folder, filename + '.h') # Outputfile for font
                png_filename = os.path.join(output_bmh_folder, filename + '.png') # Outputfile for font

                # define PILfont
                size = [width, height]

                if (args.font_height is None):
                    font_height = int(font_heights[height_idx]*1.1)
                else:
                    font_height = int(args.font_height)

                #font_height = int(height*1.1)
                
                if(print_ascii):
                    print("\n" + filename + ':')
                    
                try:
                    PILfont = ImageFont.truetype(ttf_absolute_filename, font_height)
                except Exception as ex:
                    print(f"Exception: {ex} when reading font file {ttf_absolute_filename} with height {font_height}. Skipping.")
                    continue

                # Open BMH file and start writing
                if(variable_width):
                    mywidth = "variable"
                else:
                    mywidth = str(width)
                outfile = write_bmh_head(h_filename, Font, height,mywidth)

                # the overall image, combines all characters, constructed one by one
                mode = '1'
                pic_size = (len(character_line) * (width + 10), height)
                image_pic =  Image.new(mode, pic_size, color=255)
                width_so_far = 0
                
                for char in chars:
                    # Create pixel image with PIL
                    image =  Image.new('1', size, color=255)
                    draw = ImageDraw.Draw(image)
                    draw.text((0, -yoffset), char, font=PILfont, anchor=anchor)

                    # Calculate byte arrays and write to file

                    if(variable_width):
                        [zero_col_cnt_left, zero_col_cnt_right] = calculate_char_width(image, width, height)
                        char_width = width - zero_col_cnt_right - zero_col_cnt_left
                        x_offset = zero_col_cnt_left
                        if char_width < 1:
                            char_width = 0
                            x_offset = 0
                    else:
                        char_width = width
                        x_offset = 0

                    width_array.append(str(char_width))
                    dot_array = get_pixel_byte(image, height, char_width, x_offset, print_ascii)

                    write_bmh_char(outfile, char, dot_array, progmem)
                    if(print_ascii):
                        print(char + ":")
                        print_char(image, height, char_width, x_offset)
                        
                    print_image(image_pic,width_so_far,image, height, char_width, x_offset)
                    width_so_far += char_width
                    if(variable_width):
                        width_so_far += 1

                # write tail and close bmh file
                write_bmh_tail(outfile, width_array, character_line)
                
                # write Image picture with all characters
                write_pic_file(image_pic, width_so_far, height, png_filename)

                logfile_append(logfile, filename)

        #print('-------------------------------------------------------------------------')
        print("TTF2BMH Finished")
        logfile_close(logfile)

#---------------------------------------------------------------------------------------
def print_program_header():
    print('-------------------------------------------------------------------------')
    print(' TTF2BMH Version ' + VERSION + ' (C) 2019-2020, jdmorise@yahoo.com')
    print(' ')
    print(' A conversion tool for Truetype Fonts to bitmap C header files ')
    print(' for any character for use with monochrome LCD or OLED displays ')
    print(' ')
    print('-------------------------------------------------------------------------')


#---------------------------------------------------------------------------------------
def print_license():
    print('-------------------------------------------------------------------------')
    print(' ')
    print(' (C) 2019-2020, jdmorise@yahoo.com')
    print(' ')
    print(' This program is free software: you can redistribute it and/or modify')
    print(' it under the terms of the GNU General Public License as published by')
    print(' the Free Software Foundation, either version 3 of the License, or')
    print(' (at your option) any later version.')
    print(' ')
    print(' This program is distributed in the hope that it will be useful,')
    print(' but WITHOUT ANY WARRANTY; without even the implied warranty of')
    print(' MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the')
    print(' GNU General Public License for more details.')
    print(' ')
    print(' You should have received a copy of the GNU General Public License')
    print(' along with this program.  If not, see <https://www.gnu.org/licenses/>')
    print(' ')
    print('-------------------------------------------------------------------------')


#---------------------------------------------------------------------------------------
# Search all Folders and check for filenames of Font Names, required by PIL TTF Font handler
def get_ttf_filename (Target_Font, ttf_searchfolder):
    TTF_FILES = []
    target_ttf_file = -1
    target_ttf_dir = -1
    for dirpath, dirnames, filenames in os.walk(ttf_searchfolder):
        for filename in [f for f in filenames if f.endswith(".ttf")]:
            ttf_file = {'dir': dirpath, 'filename': filename}
            TTF_FILES.append(ttf_file)

    for ttf_file in TTF_FILES:
        ttf_absolute_filename = os.path.join(ttf_file['dir'], ttf_file['filename'])
        tt = ttLib.TTFont(ttf_absolute_filename)
        fm = tt['name'].names[4].string
        Font = fm.decode('ascii', errors ='replace')

        Font = re.sub('\x00','',Font)
        if(Target_Font == Font):
            target_ttf_file =  ttf_file['filename']
            target_ttf_dir  =  ttf_file['dir']

    return target_ttf_file, target_ttf_dir

#---------------------------------------------------------------------------------------
# Write picture file
def write_pic_file(image_pic, width_so_far, height, png_filename):
    actual_x,actual_y = image_pic.size
    # print(f"Resizing image ({width_so_far},{height}) from ({actual_x},{actual_y})")
    
    if width_so_far <= 0:
        width_so_far = 0
    if (actual_x < width_so_far) or (actual_y < height):
        print(f"ERROR: truncating image ({width_so_far},{height}) to ({actual_x},{actual_y})")
        image_pic.save(png_filename)
    else:
        newimg = image_pic.crop((0,0,width_so_far,height))
        newimg.save(png_filename)

    return 0

#---------------------------------------------------------------------------------------
# Calculate full pixels from image
def get_pixel_byte(image, height, char_width, x_offset, print_ascii = False):
    dot_threshold = 127
    dot_array = []
    s = ""
    for y_s in range(int(height/8)):
        if print_ascii:
            s = "\n"
        for x_s in range(char_width):
            dot_byte = 0
            for k in range(8):
                bmf_s = image.getpixel(((x_s + x_offset), (y_s * 8 + k)))
                if(bmf_s < dot_threshold):
                    dot_byte = dot_byte + 2**k
            if print_ascii:
                dot_array.append(s+format(dot_byte,"#010b"))
                s = ""
            else:
                dot_array.append(str(dot_byte))
    return dot_array

#---------------------------------------------------------------------------------------
# Count empty columns from left
def calculate_char_width(image, width, height):
    dot_threshold = 127

    zero_col_cnt_left = 0
    for x_c in range(width):

        pxl_col_cnt = 0
        for y_c in range(height):
            bmf_s = image.getpixel((x_c, y_c))
            if(bmf_s < dot_threshold):
                pxl_col_cnt += 1

        if(pxl_col_cnt == 0):
            zero_col_cnt_left += 1
        else:
            break
# Count empty columns from left
    zero_col_cnt_right = 0
    for x_c in range(width):

        pxl_col_cnt = 0
        for y_c in range(height):
            bmf_s = image.getpixel((width-x_c-1, y_c))
            if(bmf_s < dot_threshold):
                pxl_col_cnt += 1

        if(pxl_col_cnt == 0):
            zero_col_cnt_right += 1
        else:
            break

    return [zero_col_cnt_left, zero_col_cnt_right]

#---------------------------------------------------------------------------------------
# Read character file
def read_character_file(char_filename):
    chars = []
    char_file = open(char_filename,'r')
    character_line = char_file.read().replace("\n", "")
    [chars.append(x) for x in character_line if x not in chars]
    character_line = "".join(chars)

    return [character_line,chars]

#---------------------------------------------------------------------------------------
# Search for TTF Files in given path and create array of files and directories
def search_ttf_folder(ttf_searchfolder):
    TTF_FILES = []
    for dirpath, dirnames, filenames in os.walk(ttf_searchfolder):
        for filename in [f for f in filenames if f.endswith(".ttf")]:
            ttf_file = {'dir': dirpath, 'filename': filename}
            TTF_FILES.append(ttf_file)
    return TTF_FILES

#---------------------------------------------------------------------------------------
def write_bmh_head(h_filename, Font, height, width):
# Process BMF array and create header file to be used with any C compiler
    outfile = open(h_filename,"w+")

    outfile.write("// Header File for SSD1306 characters\n")
    outfile.write("// Generated with TTF2BMH\n")
    outfile.write("// Font " +  Font + "\n")

    #print('Font: ' + Font + ', Size:' + str(height))
    outfile.write(f"// Font Size: {height} * {width}\n")
    return outfile

#---------------------------------------------------------------------------------------
#
def write_bmh_char(outfile, char, dot_array, progmem):
    # C Type declaration strings
    # Adjust for different MCU/compilers
    C_declaration_0 = 'const char bitmap_'
    if(progmem):
        C_declaration_1 = '[] PROGMEM = {'
    else:
        C_declaration_1 = '[] = {'

    C_mem_array = (','.join(dot_array))
    C_printline = C_declaration_0 + str(ord(char)) + C_declaration_1 + C_mem_array +'};'
    if ord(char) >= 32 and ord(char) < 128:  
        C_printline = C_printline + ' // char ' + char
    C_printline = C_printline + '\n'
    #print(C_printline)
    outfile.write(C_printline)

#---------------------------------------------------------------------------------------
# Write BMH Tail and close file
def write_bmh_tail(outfile, width_array, character_line):
    C_addr_array = []
    C_char_width_0 = 'const char char_width[] = {'
    C_char_width_1 = (','.join(width_array))
    C_char_width_2 = '};\n'

    outfile.write(C_char_width_0 + C_char_width_1 + C_char_width_2)

    for char in character_line:
        C_addr_array.append('&bitmap_' + str(ord(char)))

    C_addr  = (','.join(C_addr_array))
    C_address_declaration_1 = "const char* char_addr[] = {"
    C_address_declaration_2 = "};\n"

    outfile.write(C_address_declaration_1 + C_addr + C_address_declaration_2)

    outfile.close()

#---------------------------------------------------------------------------------------
#
def logfile_open(ttf_searchfolder):

    log_filename = os.path.join(ttf_searchfolder, 'ttf2bmh.log')
    log_file = open(log_filename,'w+')
    log_file.write('TTF2BMH version ' + VERSION + '(c) JD Morise\n')
    log_file.write('====================================================================\n')
    return log_file

#---------------------------------------------------------------------------------------
# Append Font name to Logfile
def logfile_append(log_file, filename):
    log_file.write(filename + '.h\n')

#---------------------------------------------------------------------------------------
# close Logfile
def logfile_close(log_file):
    log_file.write('====================================================================\n')
    log_file.close()

#---------------------------------------------------------------------------------------
# print pixel array as ASCII Art
def print_char(image, height, char_width, x_offset):
    dot_threshold = 128
    for y_s in range(height):
        ascii_bmp = ''
        for x_s in range(char_width):
            bmf_s = image.getpixel(((x_s+x_offset), y_s))
            if (bmf_s < dot_threshold):
                ascii_bmp = ascii_bmp + '#'
            else:
                ascii_bmp = ascii_bmp + '.'
        print(ascii_bmp)
    print(' ')
    return 0

#---------------------------------------------------------------------------------------
# Copy over pixels to destination image
# TODO do this
def print_image(dest_image, width_so_far, image, height, char_width, x_offset):
    dot_threshold = 128
    for y_s in range(height):
        for x_s in range(char_width):
            bmf_s = image.getpixel(((x_s+x_offset), y_s))
            if (bmf_s < dot_threshold):
                dest_image.putpixel((width_so_far+x_s,y_s),0)
    return
#---------------------------------------------------------------------------------------
# Main function handler

if (__name__ == '__main__'):
    main()
