#####################################################################################################

import mmap

#####################################################################################################

ENTIRE_FILE_LOCATION = 0
HEADER_DATA_LOCATION = ENTIRE_FILE_LOCATION +2
SMALLEST_CHARACTER_CODE_LOCATION = HEADER_DATA_LOCATION +2
LARGEST_CHARACTER_CODE_LOCATION = SMALLEST_CHARACTER_CODE_LOCATION +2
WIDTH_TABLE_LOCATION = LARGEST_CHARACTER_CODE_LOCATION +2
HEIGHT_TABLE_LOCATION = WIDTH_TABLE_LOCATION +2
DEPTH_TABLE_LOCATION = HEIGHT_TABLE_LOCATION +2
ITALIC_CORRECTION_TABLE_LOCATION = DEPTH_TABLE_LOCATION +2
LIG_KERN_TABLE_LOCATION = ITALIC_CORRECTION_TABLE_LOCATION +2
KERN_TABLE_LOCATION = LIG_KERN_TABLE_LOCATION +2
EXTENSIBLE_CHARACTER_TABLE_LOCATION = KERN_TABLE_LOCATION +2
NUMBER_OF_FONT_PARAMETER_LOCATION = EXTENSIBLE_CHARACTER_TABLE_LOCATION +2
HEADER_LOCATION = 24
CHECKSUM_LOCATION = HEADER_LOCATION
DESIGN_FONT_SIZE_LOCATION = CHECKSUM_LOCATION +4
CHARACTER_CODING_SCHEME_LOCATION = DESIGN_FONT_SIZE_LOCATION +4
FAMILY_LOCATION = CHARACTER_CODING_SCHEME_LOCATION +40
SEVEN_BIT_SAFE_FLAG_LOCATION = FAMILY_LOCATION +20

HEADER_DATA_LENGTH_MIN = 18

SLANT_LOCATION = 0
SPACING_LOCATION = SLANT_LOCATION +4
SPACE_STRETCH_LOCATION = SPACING_LOCATION +4
SPACE_SHRINK_LOCATION = SPACE_STRETCH_LOCATION +4
X_HEIGHT_LOCATION = SPACE_SHRINK_LOCATION +4
QUAD_LOCATION = X_HEIGHT_LOCATION +4
EXTRA_SPACE_LOCATION = QUAD_LOCATION +4

class TfmFile(object):

    ###############################################

    def __init__(self, tfm_file_name):

        self.tfm_file_name = tfm_file_name

        self.tfm_file = open(self.tfm_file_name, 'r+b')

        self.map = mmap.mmap(self.tfm_file.fileno(), 0)

        self.entire_file_length = self.read_unsigned_byte2(ENTIRE_FILE_LOCATION)
        self.header_data_length = self.read_unsigned_byte2(HEIGHT_TABLE_LOCATION)
        self.smallest_character_code = self.read_unsigned_byte2(SMALLEST_CHARACTER_CODE_LOCATION)
        self.largest_character_code = self.read_unsigned_byte2(LARGEST_CHARACTER_CODE_LOCATION)
        self.width_table_length = self.read_unsigned_byte2(WIDTH_TABLE_LOCATION)
        self.height_table_length = self.read_unsigned_byte2(HEIGHT_TABLE_LOCATION)
        self.depth_table_length = self.read_unsigned_byte2(DEPTH_TABLE_LOCATION)
        self.italic_correction_table_length = self.read_unsigned_byte2(ITALIC_CORRECTION_TABLE_LOCATION)
        self.lig_kern_table_length = self.read_unsigned_byte2(LIG_KERN_TABLE_LOCATION)
        self.kern_table_length = self.read_unsigned_byte2(KERN_TABLE_LOCATION)
        self.extensible_character_table_length = self.read_unsigned_byte2(EXTENSIBLE_CHARACTER_TABLE_LOCATION)
        self.number_of_font_parameter = self.read_unsigned_byte2(NUMBER_OF_FONT_PARAMETER_LOCATION)

        if self.header_data_length < HEADER_DATA_LENGTH_MIN:
            self.header_data_length = HEADER_DATA_LENGTH_MIN

        self.character_info_location = 6 + self.header_data_length
        self.width_table_location = (self.character_info_location + 
                                     self.largest_character_code -
                                     self.smallest_character_code +1)
        self.height_table_location = self.width_table_location + self.width_table_length
        self.depth_table_location = self.height_table_location + self.height_table_length
        self.italic_correction_table_location = self.depth_table_location + self.depth_table_length
        self.lig_kern_table_location = self.italic_correction_table_location + self.italic_correction_table_length
        self.kern_table_location = self.lig_kern_table_location + self.lig_kern_table_length
        self.extensible_character_table_location = self.kern_table_location + self.kern_table_length
        self.font_parameter_location = self.extensible_character_table_location + self.extensible_character_table_length

        length = self.font_parameter_location + self.number_of_font_parameter
        if self.entire_file_length != length:
            print self.entire_file_length, '!=', length
            raise NameError('Bad TFM file')

        self.character_info_location *= 4
        self.width_table_location *= 4
        self.height_table_location *= 4
        self.depth_table_location *= 4
        self.italic_correction_table_location *= 4
        self.lig_kern_table_location *= 4
        self.kern_table_location *= 4
        self.extensible_character_table_location *= 4
        self.font_parameter_location *= 4

        self.checksum = self.read_unsigned_byte4(CHECKSUM_LOCATION)
        self.design_font_size = self.read_fix_word(DESIGN_FONT_SIZE_LOCATION)
        self.character_coding_scheme = self.read_bcpl(CHARACTER_CODING_SCHEME_LOCATION)
        self.family = self.read_bcpl(FAMILY_LOCATION)

        # Read Font Parameters

        self.slant = self.read_fix_word(self.font_parameter_location + SLANT_LOCATION)
        self.spacing = self.read_fix_word(self.font_parameter_location + SPACING_LOCATION)
        self.space_stretch = self.read_fix_word(self.font_parameter_location + SPACE_STRETCH_LOCATION)
        self.space_shrink = self.read_fix_word(self.font_parameter_location + SPACE_SHRINK_LOCATION)
        self.x_height = self.read_fix_word(self.font_parameter_location + X_HEIGHT_LOCATION)
        self.quad = self.read_fix_word(self.font_parameter_location + QUAD_LOCATION)
        self.extra_space = self.read_fix_word(self.font_parameter_location + EXTRA_SPACE_LOCATION)

        # Read Chars 
        
        self.widths = []
        self.heights = []

        for c in xrange(self.smallest_character_code, self.largest_character_code +1):
            
            width_index, height_index, depth_index, italic_index, tag, remainder = self.read_char_info(c)

            width = self.read_fix_word(self.width_table_location + width_index*4)
            height = self.read_fix_word(self.height_table_location + height_index*4)

            self.widths.append(width)
            self.heights.append(height)

    ###############################################

    def read_bcpl(self, i):

        length = ord(self.map[i])

        return self.map[i+1:i+length+1]

    def read_unsigned_byte2(self, i):

        bytes = map(ord, self.map[i:i+2])

        return (bytes[0] << 8) + bytes[1]

    def read_unsigned_byte4(self, i):

        bytes = map(ord, self.map[i:i+4])

        return (((((bytes[0] << 8) + bytes[1]) << 8) + bytes[2]) << 8) + bytes[3]

    def read_fix_word(self, i):

        bytes = map(ord, self.map[i:i+4])

        # bytes = [0x7F,0xFF,0xFF,0xFF]
        # bytes = [0x80,0x0F,0xFF,0xFF]
        # bytes = [0x80,0x00,0x0,0x0]

        # print map(hex, bytes)

        number = bytes[0]
        if number >= 128:
            number -= 256
            negative = True
        else:
            negative = False
        number *= 16

        number += (bytes[1] >> 4)

        encoded_fraction = ((((bytes[1] & 0xF) << 8) + bytes[2]) << 8) + bytes[3]

        # print hex(number), hex(encoded_fraction)

        fraction = .0
        for i in xrange(20):
            if encoded_fraction & (1<<i) != 0:
                fraction += 2**(-20+i)

        # print negative, number, fraction

        if negative is True:
            number -= fraction
        else:
            number += fraction

        return number

    def read_char_info(self, k):
 
        i = self.character_info_location + k*4
 
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
 - Character coding scheme location: "%s"
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
       self.number_of_font_parameter,
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

        print 'Char 0', self.widths[0], self.heights[0]

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
