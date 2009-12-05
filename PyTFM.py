#####################################################################################################

import mmap

#####################################################################################################

ENTIRE_FILE_LENGTH_LOCATION = 0
HEADER_DATA_LENGTH_LOCATION = ENTIRE_FILE_LENGTH_LOCATION +2
SMALLEST_CHARACTER_CODE_LENGTH_LOCATION = HEADER_DATA_LENGTH_LOCATION +2
LARGEST_CHARACTER_CODE_LENGTH_LOCATION = SMALLEST_CHARACTER_CODE_LENGTH_LOCATION +2
WIDTH_TABLE_LENGTH_LOCATION = LARGEST_CHARACTER_CODE_LENGTH_LOCATION +2
HEIGHT_TABLE_LENGTH_LOCATION = WIDTH_TABLE_LENGTH_LOCATION +2
DEPTH_TABLE_LENGTH_LOCATION = HEIGHT_TABLE_LENGTH_LOCATION +2
ITALIC_CORRECTION_TABLE_LENGTH_LOCATION = DEPTH_TABLE_LENGTH_LOCATION +2
LIG_KERN_TABLE_LENGTH_LOCATION = ITALIC_CORRECTION_TABLE_LENGTH_LOCATION +2
KERN_TABLE_LENGTH_LOCATION = LIG_KERN_TABLE_LENGTH_LOCATION +2
EXTENSIBLE_CHARACTER_TABLE_LENGTH_LOCATION = KERN_TABLE_LENGTH_LOCATION +2
NUMBER_OF_FONT_PARAMETER_LOCATION = EXTENSIBLE_CHARACTER_TABLE_LENGTH_LOCATION +2
HEADER_LOCATION = 24
CHECKSUM_LOCATION = HEADER_LOCATION
DESIGN_FONT_SIZE_LOCATION = CHECKSUM_LOCATION +4
CHARACTER_CODING_SCHEME_LOCATION = DESIGN_FONT_SIZE_LOCATION +4
FAMILY_LOCATION = CHARACTER_CODING_SCHEME_LOCATION +40
SEVEN_BIT_SAFE_FLAG_LOCATION = FAMILY_LOCATION +20

class TfmFile(object):

    ###############################################

    def __init__(self, tfm_file_name):

        self.tfm_file_name = tfm_file_name

        self.tfm_file = open(self.tfm_file_name, 'r+b')

        self.map = mmap.mmap(self.tfm_file.fileno(), 0)

        self.entire_file_length = self.read_unsigned_byte2(ENTIRE_FILE_LENGTH_LOCATION)
        self.header_data_length = self.read_unsigned_byte2(HEIGHT_TABLE_LENGTH_LOCATION)
        self.smallest_character_code_length = self.read_unsigned_byte2(SMALLEST_CHARACTER_CODE_LENGTH_LOCATION)
        self.largest_character_code_length = self.read_unsigned_byte2(LARGEST_CHARACTER_CODE_LENGTH_LOCATION)
        self.width_table_length = self.read_unsigned_byte2(WIDTH_TABLE_LENGTH_LOCATION)
        self.height_table_length = self.read_unsigned_byte2(HEIGHT_TABLE_LENGTH_LOCATION)
        self.depth_table_length = self.read_unsigned_byte2(DEPTH_TABLE_LENGTH_LOCATION)
        self.italic_correction_table_length = self.read_unsigned_byte2(ITALIC_CORRECTION_TABLE_LENGTH_LOCATION)
        self.lig_kern_table_length = self.read_unsigned_byte2(LIG_KERN_TABLE_LENGTH_LOCATION)
        self.kern_table_length = self.read_unsigned_byte2(KERN_TABLE_LENGTH_LOCATION)
        self.extensible_character_table_length = self.read_unsigned_byte2(EXTENSIBLE_CHARACTER_TABLE_LENGTH_LOCATION)
        self.number_of_font_parameter = self.read_unsigned_byte2(NUMBER_OF_FONT_PARAMETER_LOCATION)

        self.checksum = self.read_unsigned_byte4(CHECKSUM_LOCATION)
        self.design_font_size = self.read_fix_word(DESIGN_FONT_SIZE_LOCATION)
        self.character_coding_scheme = self.map[CHARACTER_CODING_SCHEME_LOCATION:FAMILY_LOCATION]
        self.family = self.map[FAMILY_LOCATION:SEVEN_BIT_SAFE_FLAG_LOCATION]

    ###############################################

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

        # print map(hex, bytes)

        number = bytes[0]
        if number >= 128:
            number = 256 - number
            negative = True
        else:
            negative = False
        number <<= 4

        number += (bytes[1] >> 4)

        encoded_fraction = ((((bytes[1] & 0xF) << 8) + bytes[2]) << 8) + bytes[3]

        # print hex(number), hex(encoded_fraction)

        fraction = .0
        for i in xrange(20):
            if encoded_fraction & (1<<i) != 0:
                fraction += 2**(-i-1)

        # print negative, number, fraction

        number += fraction
        
        if negative is True:
            number = -number

        return number

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
 - Character coding scheme location: " %s"
 - Family: "%s"
''' % (self.tfm_file_name,
       self.entire_file_length,
       self.header_data_length,
       self.smallest_character_code_length,
       self.largest_character_code_length,
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
       self.family)

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
