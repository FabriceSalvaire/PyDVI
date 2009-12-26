#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
#  - 26/12/2009 fabrice
#
#####################################################################################################

#####################################################################################################

import mmap

#####################################################################################################

NO_TAG, LIG_TAG, LIST_TAG, EXT_TAG = range(4)

KERN_OPCODE = 128

#####################################################################################################

def word_ptr(base, ptr):
    return 4*(base + ptr)

#####################################################################################################

class TfmParser(object):

    ###############################################

    def __init__(self, tfm_file_name):

        self.tfm_file_name = tfm_file_name

        self.tfm_file = open(self.tfm_file_name, 'rb')

        self.map = mmap.mmap(self.tfm_file.fileno(), 0)

        self.read_lengths()
        self.read_header()
        self.read_font_parameters()

        # self.tfm.print_summary()

        for c in xrange(self.smallest_character_code, self.largest_character_code +1):
            self.process_char(c)

        for i in xrange(self.lig_kern_table_length):

            base = word_ptr(self.lig_kern_table_ptr, i)

            skip_byte, next_char, op_byte, remainder = map(ord, self.map[base:base+4])

            print i, skip_byte, chr(next_char), op_byte, remainder

            if op_byte >= KERN_OPCODE:

                kern_ptr = 256*(op_byte-KERN_OPCODE) + remainder
                kern = self.read_fix_word(word_ptr(self.kern_table_ptr, kern_ptr))

                print 'kern', i, next_char, chr(next_char), kern_ptr, kern

            else:

                a = op_byte >> 2
                b = op_byte & 0x02
                c = op_byte & 0x01

                print 'lig', a, b, c, chr(next_char), remainder

    ###############################################

    def read_lengths(self):

        # A font may contain as many as 256 characters.
        #   sc - 1 <= lc <= 255
        # extensible_character_table_length <= 256

        self.ptr = 0

        number_of_items = 12

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
         self.font_parameter_length) = map(lambda i: self.read_unsigned_byte2(self.ptr),
                                           range(number_of_items))

        self.number_of_chars = self.largest_character_code - self.smallest_character_code +1

        header_data_length_min = 18
        self.header_data_length = max(header_data_length_min, self.header_data_length)

        # Compute table pointers of blocs of 4 bytes

        self.header_ptr = 2*number_of_items
        # Convert number_of_items * 2 bytes to 4 bytes
        self.character_info_ptr = number_of_items/2 + self.header_data_length
        self.width_table_ptr = self.character_info_ptr + self.number_of_chars
        self.height_table_ptr = self.width_table_ptr + self.width_table_length
        self.depth_table_ptr = self.height_table_ptr + self.height_table_length
        self.italic_correction_table_ptr = self.depth_table_ptr + self.depth_table_length
        self.lig_kern_table_ptr = self.italic_correction_table_ptr + self.italic_correction_table_length
        self.kern_table_ptr = self.lig_kern_table_ptr + self.lig_kern_table_length
        self.extensible_character_table_ptr = self.kern_table_ptr + self.kern_table_length
        self.font_parameter_ptr = self.extensible_character_table_ptr + self.extensible_character_table_length

        length = self.font_parameter_ptr + self.font_parameter_length
        if self.entire_file_length != length:
            raise NameError('Bad TFM file')

    ###############################################

    def read_header(self):

        # character_coding_scheme_length = 40
        # family_length= 20

        self.ptr = self.header_ptr

        checksum = self.read_unsigned_byte4(self.ptr)
        design_font_size = self.read_fix_word(self.ptr)

        if self.header_data_length > self.ptr:
            character_coding_scheme = self.read_bcpl(self.ptr)
        else:
            character_coding_scheme = None
        
        if self.header_data_length > self.ptr:
            family = self.read_bcpl(self.ptr)
        else:
            family = None

        if self.header_data_length > self.ptr:
            seven_bit_safe_flag = self.read_unsigned_byte4(self.ptr)
            # Fixme: complete

        self.tfm = Tfm(self.smallest_character_code,
                       self.largest_character_code,
                       checksum,
                       design_font_size,
                       character_coding_scheme,
                       family)

    ###############################################

    def read_font_parameters(self):
                 
        self.ptr = self.font_parameter_ptr
 
        self.tfm.set_font_parameters(map(lambda i: self.read_fix_word(self.ptr),
                                         range(self.font_parameter_length)))

        if self.tfm.character_coding_scheme == 'TeX math symbols':
            self.tfm.set_math_symbols_parameters(map(lambda i: self.read_fix_word(self.ptr),
                                                     range(15)))

        elif self.tfm.character_coding_scheme == 'TeX math extension':
            self.tfm.set_math_extension_parameters(map(lambda i: self.read_fix_word(self.ptr),
                                                       range(6)))

    ###############################################

    def process_char(self, c):
        
        width_ptr, height_ptr, depth_ptr, italic_ptr, tag, remainder = self.read_char_info(c)

        if width_ptr == 0: # unvalid char
            return

        width = self.read_fix_word(word_ptr(self.width_table_ptr, width_ptr))
        
        if height_ptr == 0:
            height = self.read_fix_word(word_ptr(self.height_table_ptr, height_ptr))
        else:
            height = 0

        if depth_ptr == 0:
            depth = self.read_fix_word(word_ptr(self.depth_table_ptr, depth_ptr))
        else:
            depth = 0

        if italic_ptr == 0:
            italic_correction = self.read_fix_word(word_ptr(self.italic_correction_table_ptr, italic_ptr))
        else:
            italic_correction = 0

        next_larger_character = None

        tfm_char = TfmChar(c,
                           width,
                           height,
                           depth,
                           italic_correction)

        tfm_char.print_summary()

        print 'tag', tag
        
        if tag == LIG_TAG:
            lig_kern_program_ptr = remainder
            print 'lig_kern_program_ptr', lig_kern_program_ptr
            
        elif tag == LIST_TAG:
            next_larger_character = remainder
            print 'next_larger_character', next_larger_character

        elif tag == EXT_TAG:
            top, mid, bot, rep = self.read_extensible_recipe(remainder)
            print 'ext_tag', top, mid, bot, rep

    ###############################################

    def read_four_bytes(self, i):

        return map(ord, self.map[i:i+4])

    ###############################################

    def read_bcpl(self, i):

        length = ord(self.map[i])
        i += 1
        self.ptr = i + length

        return self.map[i:self.ptr]

    ###############################################

    def read_unsigned_byte2(self, i):

        self.ptr = i + 2

        bytes = map(ord, self.map[i:self.ptr])

        return (bytes[0] << 8) + bytes[1]

    ###############################################

    def read_unsigned_byte4(self, i):

        self.ptr = i + 4

        bytes = map(ord, self.map[i:self.ptr])

        return (((((bytes[0] << 8) + bytes[1]) << 8) + bytes[2]) << 8) + bytes[3]

    ###############################################

    def read_fix_word(self, i):

        # A fix word is a signed quantity, with the two's complement of the entire word used to
        # represent negation.  Of the 32 bits in fix word, exactly 12 are to the left of the binary
        # point.

        self.ptr = i + 4

        bytes = map(ord, self.map[i:self.ptr])

        fix_word = bytes[0]
        if fix_word >= 128:
            fix_word -= 256
        fix_word *= 2**24

        fix_word += (((bytes[1] << 8) + bytes[2]) << 8) + bytes[3]

        return float(fix_word)/2**20

    ###############################################

    def read_char_info(self, c):
 
        i = word_ptr(self.character_info_ptr, c - self.smallest_character_code)
 
        bytes = self.read_four_bytes(i)

        width_ptr  = bytes[0]
        height_ptr = bytes[1] >> 4
        depth_ptr  = bytes[1] & 0xF
        italic_ptr = bytes[2] >> 6
        tag        = bytes[2] & 0x3
        remainder  = bytes[3]

        return width_ptr, height_ptr, depth_ptr, italic_ptr, tag, remainder

    ###############################################

    def read_extensible_recipe(self, c):
 
        i = word_ptr(self.extensible_character_table_ptr, c)

        return self.read_four_bytes(i)

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
# End
#
#####################################################################################################
