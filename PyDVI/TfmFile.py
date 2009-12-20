#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################

import mmap

#####################################################################################################

HEADER_DATA_LENGTH_MIN = 18

CHARACTER_CODING_SCHEME_LENGTH = 40
FAMILY_LENGTH= 20

HEADER_INDEX = 24
CHECKSUM_INDEX = HEADER_INDEX
DESIGN_FONT_SIZE_INDEX = CHECKSUM_INDEX +4
CHARACTER_CODING_SCHEME_INDEX = DESIGN_FONT_SIZE_INDEX +4
FAMILY_INDEX = CHARACTER_CODING_SCHEME_INDEX + CHARACTER_CODING_SCHEME_LENGTH
SEVEN_BIT_SAFE_FLAG_INDEX = FAMILY_INDEX + FAMILY_LENGTH

def word_index(base, index):
    return (base + index)*4

#####################################################################################################

class TfmFile(object):

    ###############################################

    def __init__(self, tfm_file_name):

        self.tfm_file_name = tfm_file_name

        self.tfm_file = open(self.tfm_file_name, 'r+b')

        self.map = mmap.mmap(self.tfm_file.fileno(), 0)

        # Read lengths

        (self.entire_file_length,
         self.header_data_length,
         self.smallest_character_code,
         self.largest_character_code,
         self.width_table_length,
         self.height_table_length,
         self.depth_table_length,
         self.italic_correction_table_length,
         self.lig_kern_table_length,
         self.kern_table_length,
         self.extensible_character_table_length,
         self.font_parameter_length) =  map(lambda i: self.read_unsigned_byte2(2*i), range(12))

        if self.header_data_length < HEADER_DATA_LENGTH_MIN:
            self.header_data_length = HEADER_DATA_LENGTH_MIN

        # Compute index

        self.character_info_index = 6 + self.header_data_length
        self.width_table_index = (self.character_info_index + 
                                  self.largest_character_code - self.smallest_character_code +1)
        self.height_table_index = self.width_table_index + self.width_table_length
        self.depth_table_index = self.height_table_index + self.height_table_length
        self.italic_correction_table_index = self.depth_table_index + self.depth_table_length
        self.lig_kern_table_index = self.italic_correction_table_index + self.italic_correction_table_length
        self.kern_table_index = self.lig_kern_table_index + self.lig_kern_table_length
        self.extensible_character_table_index = self.kern_table_index + self.kern_table_length
        self.font_parameter_index = self.extensible_character_table_index + self.extensible_character_table_length

        length = self.font_parameter_index + self.font_parameter_length
        if self.entire_file_length != length:
            # print self.entire_file_length, '!=', length
            raise NameError('Bad TFM file')

        self.checksum = self.read_unsigned_byte4(CHECKSUM_INDEX)
        self.design_font_size = self.read_fix_word(DESIGN_FONT_SIZE_INDEX)
        self.character_coding_scheme = self.read_bcpl(CHARACTER_CODING_SCHEME_INDEX)
        self.family = self.read_bcpl(FAMILY_INDEX)

        # Read Font Parameters

        (self.slant,
         self.spacing,
         self.space_stretch,
         self.space_shrink,
         self.x_height,
         self.quad,
         self.extra_space) = map(lambda i: self.read_fix_word(word_index(self.font_parameter_index, i)),
                                 range(self.font_parameter_length))
         
        # Read Chars 
        
        self.widths = []
        self.heights = []

        for c in xrange(self.smallest_character_code, self.largest_character_code +1):
            
            width_index, height_index, depth_index, italic_index, tag, remainder = self.read_char_info(c)

            width = self.read_fix_word(word_index(self.width_table_index, width_index))
            height = self.read_fix_word(word_index(self.height_table_index, height_index))

            self.widths.append(width)
            self.heights.append(height)

    ###############################################

    def read_bcpl(self, i):

        length = ord(self.map[i])

        k = i + 1

        return self.map[k:k+length]

    ###############################################

    def read_unsigned_byte2(self, i):

        bytes = map(ord, self.map[i:i+2])

        return (bytes[0] << 8) + bytes[1]

    ###############################################

    def read_unsigned_byte4(self, i):

        bytes = map(ord, self.map[i:i+4])

        return (((((bytes[0] << 8) + bytes[1]) << 8) + bytes[2]) << 8) + bytes[3]

    ###############################################

    def read_fix_word(self, i):

        # x / 2**20 ?

        bytes = map(ord, self.map[i:i+4])

        # bytes = [0x7F,0xFF,0xFF,0xFF]
        # bytes = [0x80,0x0F,0xFF,0xFF]
        # bytes = [0x80,0x00,0x0,0x0]

        integral_part = bytes[0]
        if integral_part >= 128:
            integral_part -= 256
            negative = True
        else:
            negative = False
        integral_part *= 16

        integral_part += (bytes[1] >> 4)

        fractional_part = float(((((bytes[1] & 0xF) << 8) + bytes[2]) << 8) + bytes[3])
        fractional_part /= 2**20 # 1 << 20

        # print negative, integral_part, fractional_part

        if negative is True:
            return integral_part - fractional_part
        else:
            return integral_part + fractional_part

    ###############################################

    def read_char_info(self, k):
 
        i = word_index(self.character_info_index, k)
 
        bytes = map(ord, self.map[i:i+4])

        width_index  = bytes[0]
        height_index = bytes[1] >> 4
        depth_index  = bytes[1] & 0xF
        italic_index = bytes[2] >> 6
        tag          = bytes[2] & 0x3
        remainder    = bytes[3]

        return width_index, height_index, depth_index, italic_index, tag, remainder

    ###############################################

    def print_summary(self):

        print '''
TFM %s

 - Length of the entire file, in words: %u 
 - Length of the header data, in words: %u 
 - Smallest character code in the font: %u 
 - Largest character code in the font: %u 
 - Number of words in the width table: %u 
 - Number of words in the height table: %u 
 - Number of words in the depth table: %u 
 - Number of words in the italic correction table: %u
 - Number of words in the lig/kern table: %u 
 - Number of words in the kern table: %u 
 - Number of words in the extensible character table: %u 
 - Number of font parameter words: %u 

 - Checksum: %u
 - Design Font Size: %f
 - Character coding scheme: "%s"
 - Family: "%s"

Font Parameters:
 - Slant: %f
 - Spacing: %f
 - Space Stretch: %f
 - Space Shrink: %f
 - X Height: %f
 - Quad: %f
 - Extra Space: %f
''' % (self.tfm_file_name,
       self.entire_file_length,
       self.header_data_length,
       self.smallest_character_code,
       self.largest_character_code,
       self.width_table_length,
       self.height_table_length,
       self.depth_table_length,
       self.italic_correction_table_length,
       self.lig_kern_table_length,
       self.kern_table_length,
       self.extensible_character_table_length,
       self.font_parameter_length,
       self.checksum,
       self.design_font_size,
       self.character_coding_scheme,
       self.family,
       self.slant,
       self.spacing,
       self.space_stretch,
       self.space_shrink,
       self.x_height,
       self.quad,
       self.extra_space)

        print 'Char 65', self.widths[65], self.heights[65]

#####################################################################################################
#
#                                               Test
#
#####################################################################################################
        
if __name__ == '__main__':

    # subprocess.call('kpsewhich', 'cmr10.tfm')

    from optparse import OptionParser

    usage = 'usage: %prog [options]'

    parser = OptionParser(usage)

    opt, args = parser.parse_args()

    tfm_file_name = args[0]

    tfm_file = TfmFile(tfm_file_name)

    tfm_file.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
