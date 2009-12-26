#####################################################################################################

import mmap

#####################################################################################################

class TfmChar(object):

    ###############################################

    def __init__(self,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction):

        self.char_code = char_code
        self.width = width
        self.height = height
        self.depth = depth
        self.italic_correction = italic_correction

    ###############################################

    def print_summary(self):

        print '''
Char %u %s
 - width             %.3f
 - height            %.3f
 - depth             %.3f
 - italic correction %.3f
''' % (self.char_code, chr(self.char_code),
       self.width,
       self.height,
       self.depth,
       self.italic_correction,
       )

#####################################################################################################

class Tfm(object):

    ###############################################

    def __init__(self, 
                 smallest_character_code,
                 largest_character_code,
                 checksum,
                 design_font_size,
                 character_coding_scheme,
                 family):

        self.smallest_character_code = smallest_character_code
        self.largest_character_code = largest_character_code
        self.checksum = checksum
        self.design_font_size = design_font_size
        self.character_coding_scheme = character_coding_scheme
        self.family = family

    ###############################################

    def set_font_parameters(self, parameters):

        (self.slant,
         self.spacing,
         self.space_stretch,
         self.space_shrink,
         self.x_height,
         self.quad,
         self.extra_space) = parameters

    ###############################################

    def set_math_symbols_parameters(self, parameters):
          
        (self.num1,
         self.num2,
         self.num3,
         self.denom1,
         self.denom2,
         self.sup1,
         self.sup2,
         self.sup3,
         self.sub1,
         self.sub2,
         self.supdrop,
         self.subdrop,
         self.delim1,
         self.delim2,
         self.axis_height) = parameters

    ###############################################

    def set_math_extension_parameters(self, parameters):

        self.default_rule_thickness = parameters[0]
        self.big_op_spacing = parameters[1:]

    ###############################################

    def print_summary(self):

        print '''
TFM %s

 - Smallest character code in the font: %u 
 - Largest character code in the font: %u 

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
''' % (self.smallest_character_code,
       self.largest_character_code,
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

#####################################################################################################

HEADER_ITEMS = 12

HEADER_DATA_LENGTH_MIN = 18

CHARACTER_CODING_SCHEME_LENGTH = 40
FAMILY_LENGTH= 20

HEADER_INDEX = 24
CHECKSUM_INDEX = HEADER_INDEX
DESIGN_FONT_SIZE_INDEX = CHECKSUM_INDEX +4
CHARACTER_CODING_SCHEME_INDEX = DESIGN_FONT_SIZE_INDEX +4
FAMILY_INDEX = CHARACTER_CODING_SCHEME_INDEX + CHARACTER_CODING_SCHEME_LENGTH
SEVEN_BIT_SAFE_FLAG_INDEX = FAMILY_INDEX + FAMILY_LENGTH

NO_TAG, LIG_TAG, LIST_TAG, EXT_TAG = range(4)

KERN_OPCODE = 128

#####################################################################################################

def word_index(base, index):
    return 4*(base + index)

#####################################################################################################

class TfmParser(object):

    ###############################################

    def __init__(self, tfm_file_name):

        self.tfm_file_name = tfm_file_name

        self.tfm_file = open(self.tfm_file_name, 'r+b')

        self.map = mmap.mmap(self.tfm_file.fileno(), 0)

        self.read_lengths()
        self.read_header()
        self.read_font_parameters()

        # self.tfm.print_summary()

        for c in xrange(self.smallest_character_code, self.largest_character_code +1):
            self.process_char(c)

        for i in xrange(self.lig_kern_table_length):

            base = word_index(self.lig_kern_table_index, i)

            skip_byte, next_char, op_byte, remainder = map(ord, self.map[base:base+4])

            # print i, skip_byte, chr(next_char), op_byte, remainder

            if op_byte >= KERN_OPCODE:

                kern_index = 256*(op_byte-KERN_OPCODE) + remainder
                kern = self.read_fix_word(word_index(self.kern_table_index, kern_index))

                print 'kern', next_char, chr(next_char), kern_index, kern

    ###############################################

    def read_lengths(self):

        # A font may contain as many as 256 characters.

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
         self.font_parameter_length) =  map(lambda i: self.read_unsigned_byte2(2*i), range(HEADER_ITEMS))

        self.number_of_chars = self.largest_character_code - self.smallest_character_code +1

        if self.header_data_length < HEADER_DATA_LENGTH_MIN:
            self.header_data_length = HEADER_DATA_LENGTH_MIN

        # Compute index

        # HEADER_ITEMS*2/4
        self.character_info_index = HEADER_ITEMS/2 + self.header_data_length
        self.width_table_index = self.character_info_index + self.number_of_chars
        self.height_table_index = self.width_table_index + self.width_table_length
        self.depth_table_index = self.height_table_index + self.height_table_length
        self.italic_correction_table_index = self.depth_table_index + self.depth_table_length
        self.lig_kern_table_index = self.italic_correction_table_index + self.italic_correction_table_length
        self.kern_table_index = self.lig_kern_table_index + self.lig_kern_table_length
        self.extensible_character_table_index = self.kern_table_index + self.kern_table_length
        self.font_parameter_index = self.extensible_character_table_index + self.extensible_character_table_length

        length = self.font_parameter_index + self.font_parameter_length
        if self.entire_file_length != length:
            raise NameError('Bad TFM file')

    ###############################################

    def read_header(self):

        checksum = self.read_unsigned_byte4(CHECKSUM_INDEX)
        design_font_size = self.read_fix_word(DESIGN_FONT_SIZE_INDEX)

        if self.header_data_length > CHARACTER_CODING_SCHEME_INDEX:
            character_coding_scheme = self.read_bcpl(CHARACTER_CODING_SCHEME_INDEX)
        else:
            character_coding_scheme = None
        
        if self.header_data_length > FAMILY_INDEX:
            family = self.read_bcpl(FAMILY_INDEX)
        else:
            family = None

        if self.header_data_length > SEVEN_BIT_SAFE_FLAG_INDEX:
            seven_bit_safe_flag = self.read_unsigned_byte4(SEVEN_BIT_SAFE_FLAG)
            # Fixme: complete

        self.tfm = Tfm(self.smallest_character_code,
                       self.largest_character_code,
                       checksum,
                       design_font_size,
                       character_coding_scheme,
                       family)

    ###############################################

    def read_font_parameters(self):
                 
        base = self.font_parameter_index
 
        # Fixme: func = lambda ...
        self.tfm.set_font_parameters(map(lambda i: self.read_fix_word(word_index(base, i)),
                                         range(self.font_parameter_length)))

        base += self.font_parameter_length

        if self.tfm.character_coding_scheme == 'TeX math symbols':
            self.tfm.set_math_symbols_parameters(map(lambda i: self.read_fix_word(word_index(base, i)),
                                                     range(15)))

        elif self.tfm.character_coding_scheme == 'TeX math extension':
            self.tfm.set_math_extension_parameters(map(lambda i: self.read_fix_word(word_index(base, i)),
                                                       range(6)))

    ###############################################

    def process_char(self, c):
        
        width_index, height_index, depth_index, italic_index, tag, remainder = self.read_char_info(c)

        width = self.read_fix_word(word_index(self.width_table_index, width_index))
        height = self.read_fix_word(word_index(self.height_table_index, height_index))
        depth = self.read_fix_word(word_index(self.depth_table_index, depth_index))
        italic_correction = self.read_fix_word(word_index(self.italic_correction_table_index, italic_index))

        next_larger_character = None

        if tag == LIST_TAG:
            next_larger_character = remainder

        elif tag == EXT_TAG:
            top, mid, bot, rep = self.read_extensible_recipe(remainder)

        tfm_char = TfmChar(c,
                           width,
                           height,
                           depth,
                           italic_correction)

        tfm_char.print_summary()

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

        integral_part += ((((bytes[1] & 0xF) << 8) + bytes[2]) << 8) + bytes[3]
        integral_part = float(integral_part)/2**20

        return integral_part

        # fractional_part = float(((((bytes[1] & 0xF) << 8) + bytes[2]) << 8) + bytes[3])
        # fractional_part /= 2**20
        # 
        # # print negative, integral_part, fractional_part
        # 
        # if negative is True:
        #     return integral_part - fractional_part
        # else:
        #     return integral_part + fractional_part

    ###############################################

    def read_char_info(self, c):
 
        i = word_index(self.character_info_index, c - self.smallest_character_code)
 
        bytes = map(ord, self.map[i:i+4])

        width_index  = bytes[0]
        height_index = bytes[1] >> 4
        depth_index  = bytes[1] & 0xF
        italic_index = bytes[2] >> 6
        tag          = bytes[2] & 0x3
        remainder    = bytes[3]

        return width_index, height_index, depth_index, italic_index, tag, remainder

    ###############################################

    def read_extensible_recipe(self, c):
 
        i = word_index(self.extensible_character_table_index, c)

        return map(ord, self.map[i:i+4])

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
       )

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

    tfm_file = TfmParser(tfm_file_name)

    tfm_file.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
