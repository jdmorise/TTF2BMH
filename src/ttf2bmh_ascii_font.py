#-------------------------------------------------------------------------
# 
#  (C) 2019, jdmorise@yahoo.com
#  
# This software is part of the TTF2BMH software package to generate bitmap 
# header files for usage of simple OLED or LCD displays with microprocessors
# 
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
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

import os
import sys
import subprocess
from shutil import copyfile

def main(): 
    
    # Tab to iterate over all Font files and process them

    font_heights = [24, 32, 40, 48, 56, 64]   
    font_yoffsets = [3, 5, 7, 8, 9, 10]
     
    height_indices = range(len(font_heights))

    start_addr = 17
    dot_threshold = str(10)

    Fonts = ['Arial','Courier New','Times New Roman','Calibri','InkFree']
   
    
    ttf_filepath = "..\\bmh_fonts_nonfree"
    
    height=32
    
    for Font in Fonts: 
         for height_idx in height_indices: 
            height = font_heights[height_idx]
            yoffset = font_yoffsets[height_idx]

            if not (os.path.exists(ttf_filepath + '\\' + Font)): 

                    os.mkdir(ttf_filepath + '\\' + Font)

            ttf_fontpath = ttf_filepath + '\\' + Font  

            if not (os.path.exists(ttf_fontpath + '\\' + 'bmfc')): 

                    os.mkdir(ttf_fontpath + '\\' + 'bmfc')

            if not (os.path.exists(ttf_fontpath + '\\' + 'bmh')): 

                    os.mkdir(ttf_fontpath + '\\' + 'bmh')

            # Filename Definitions
            filename = Font + '_ascii_' + str(height) # General Filename 
            fnt_filename = ttf_fontpath + '\\' + 'bmfc\\' + filename + '.fnt' # Outputfile for BMF Font 
            tga_filename = ttf_fontpath + '\\' + 'bmfc\\' + filename + '_0.tga' # Outputfile for BMF TGA
            bmfc_filename = ttf_fontpath + '\\' + 'bmfc\\' + filename + '.bmfc' # Configuration File for BMF
            bmfc_initial_filename = '..\\bmfont_char_' + str(height) + '.bmfc'
            h_filename = ttf_fontpath + '\\' + 'bmh' + '\\' + filename + '.h' # Outputfile for font 

            # Copy BMFC File and add fontName information
            copyfile(bmfc_initial_filename, bmfc_filename)

            bmfc_file = open(bmfc_filename,'a+')
            bmfc_file.write('fontName=' + Font + '\n')
            bmfc_file.close()

            # Start BMF process 

            subprocess.call(['..//bmfont64.exe','-c',bmfc_filename,'-t','..//characters_ascii.txt','-o',fnt_filename])

            # Parse fnt file with font description 

            fnt_file = open(fnt_filename,'r')

            WIDTH = []
            HEIGHT = [] 
            X = []
            XOFFSET = [] 
            YOFFSET = []
            CHAR_ID = []

            for line in fnt_file: 
                if('scaleW' in line): 
                    l_str = line.split(' ')
                    for l_str_s in l_str: 
                        if('scaleW' in l_str_s): 
                            scalew = int(l_str_s.split('=')[1])
                if('char id' in line): 
                    l_str = line.split(' ')
                    for l_str_s in l_str: 
                        if 'x=' in l_str_s: 
                            X.append(l_str_s.split('=')[1]) 
                        if 'width=' in l_str_s: 
                            WIDTH.append(l_str_s.split('=')[1])
                        if 'height=' in l_str_s: 
                            HEIGHT.append(l_str_s.split('=')[1])
                        if 'xoffset=' in l_str_s: 
                            XOFFSET.append(l_str_s.split('=')[1])
                        if 'id=' in l_str_s: 
                            CHAR_ID.append(l_str_s.split('=')[1])
                        if 'yoffset=' in l_str_s: 
                            YOFFSET.append(l_str_s.split('=')[1])

            # Parsing full TGA file to internal array

            BMF = []
            i = 0
        # bitmap_char_s = bitmap_char[char_idx]
            bmf_file = open(tga_filename,'r',errors='replace')
            byte = bmf_file.read(1)
            while byte != "":
                BMF.append(byte)
                byte = bmf_file.read(1)
            bmf_file.close()    

            # Process BMF array and create header file to be used with any C compiler

            outfile = open(h_filename,"w+")

            outfile.write("// Header File for SSD1306 characters\n")
            outfile.write("// Generated with TTF2BMH\n") 
            outfile.write("// Font " +  Font + "\n") 
            outfile.write("// Font Size: " + str(height) + "\n")
            C_char_width_0 = 'static const uint8_t char_width[] = {'
            C_char_width_1 = ''
            C_char_width_2 = '};\n'
            width_array = []
            C_addr_array = []

            for i in range(len(CHAR_ID)): 

                dot_array = []
                

                #yoffset = int((height - int(HEIGHT[i]))/2)
                yoffset = 5
                for y_s in range(int(height/8)): 
                    for x_s in range(int(WIDTH[i])+1):
                        dot_byte = 0
                        for k in range(8): 
                            if(BMF[start_addr + int(X[i]) + x_s + (y_s * 8 + k + yoffset) * scalew] > dot_threshold): 
                                dot_byte = dot_byte + 2**k
                        dot_array.append(str(dot_byte))

                C_mem_array = (','.join(dot_array))
                
                if(int(CHAR_ID[i]) < 127): 
                    C_declaration_0 = 'static const uint8_t bitmap_' 
                    C_declaration_1 = '[] PROGMEM = {'
                    
                    C_printline = C_declaration_0 + CHAR_ID[i] + C_declaration_1 + C_mem_array +'};\n'
                    #print(C_printline)
                    outfile.write(C_printline)

                    width_array.append(str(int(WIDTH[i])+1))
                    C_addr_array.append('&bitmap_' + CHAR_ID[i]) 
            #Write Cahracter width to file       
            C_char_width_1 = (','.join(width_array))
            outfile.write(C_char_width_0 + C_char_width_1 + C_char_width_2)
            # Write Adress´pointer
            C_addr  = (','.join(C_addr_array)) 
            C_address_declaration_1 = "static const char* char_addr[] = {" 
            C_address_declaration_2 = "};\n"
            
            outfile.write(C_address_declaration_1 + C_addr + C_address_declaration_2)


            outfile.close()   

            print(filename + '.h written')

if (__name__ == '__main__'):
    main()