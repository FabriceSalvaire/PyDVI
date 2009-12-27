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

from DviStream import *
from Tfm import *

#####################################################################################################

NO_TAG, LIG_TAG, LIST_TAG, EXT_TAG = range(4)

KERN_OPCODE = 128

#####################################################################################################

def word_ptr(base, index):
    return base + 4*index

#####################################################################################################

class TfmParser(DviFileStream):

    ###############################################

    def __init__(self, font_name, tfm_filename):

        super(TfmParser, self).__init__(tfm_filename)

        self.font_name = font_name

        self.read_lengths()
        self.read_header()
        self.read_font_parameters()

        # for c in xrange(self.smallest_character_code, self.largest_character_code +1):
        #     self.process_char(c)
        # 
        # for i in xrange(self.lig_kern_table_length):
        # 
        #     position = word_ptr(self.lig_kern_table_ptr, i)
        # 
        #     skip_byte, next_char, op_byte, remainder = self.read_four_byte_numbers(position)
        # 
        #     print i, skip_byte, chr(next_char), op_byte, remainder
        # 
        #     if op_byte >= KERN_OPCODE:
        # 
        #         kern_index = 256*(op_byte-KERN_OPCODE) + remainder
        #         kern = self.read_fix_word(word_ptr(self.kern_table_ptr, kern_index))
        # 
        #         print 'kern', i, next_char, chr(next_char), kern_ptr, kern
        # 
        #     else:
        # 
        #         a = op_byte >> 2
        #         b = op_byte & 0x02
        #         c = op_byte & 0x01
        # 
        #         print 'lig', a, b, c, chr(next_char), remainder

    ###############################################

    def read_lengths(self):

        # A font may contain as many as 256 characters.
        #   sc - 1 <= lc <= 255
        # extensible_character_table_length <= 256

        self.seek(0)

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
         self.font_parameter_length) = self.repeat(self.read_unsigned_byte2, number_of_items)

        self.number_of_chars = self.largest_character_code - self.smallest_character_code +1

        header_data_length_min = 18
        self.header_data_length = max(header_data_length_min, self.header_data_length)

        self.print_summary()

        # Compute table pointers

        self.header_ptr = number_of_items*2 # bytes
        self.character_info_ptr = word_ptr(self.header_ptr, self.header_data_length)
        self.width_table_ptr = word_ptr(self.character_info_ptr, self.number_of_chars)
        self.height_table_ptr = word_ptr(self.width_table_ptr, self.width_table_length)
        self.depth_table_ptr = word_ptr(self.height_table_ptr, self.height_table_length)
        self.italic_correction_table_ptr = word_ptr(self.depth_table_ptr, self.depth_table_length)
        self.lig_kern_table_ptr = word_ptr(self.italic_correction_table_ptr, self.italic_correction_table_length)
        self.kern_table_ptr = word_ptr(self.lig_kern_table_ptr, self.lig_kern_table_length)
        self.extensible_character_table_ptr = word_ptr(self.kern_table_ptr, self.kern_table_length)
        self.font_parameter_ptr = word_ptr(self.extensible_character_table_ptr, self.extensible_character_table_length)

        length = word_ptr(self.font_parameter_ptr, self.font_parameter_length)
        if length != word_ptr(0, self.entire_file_length):
            raise NameError('Bad TFM file')

    ###############################################

    def read_header(self):

        character_coding_scheme_length = 40
        family_length= 10

        self.seek(self.header_ptr)

        checksum = self.read_unsigned_byte4()
        design_font_size = self.read_fix_word()
        
        position = self.tell()

        if position < self.character_info_ptr:
            character_coding_scheme = self.read_bcpl()
        else:
            character_coding_scheme = None

        position += character_coding_scheme_length

        if position < self.character_info_ptr:
            family = self.read_bcpl(position)
        else:
            family = None

        position += family_length

        if position < self.character_info_ptr:
            seven_bit_safe_flag = self.read_unsigned_byte4(position)
            # Fixme: complete

        self.tfm = Tfm(self.font_name,
                       self.smallest_character_code,
                       self.largest_character_code,
                       checksum,
                       design_font_size,
                       character_coding_scheme,
                       family)

    ###############################################

    def read_font_parameters(self):
                 
        self.seek(self.font_parameter_ptr)
 
        self.tfm.set_font_parameters(self.repeat(self.read_fix_word, self.font_parameter_length))

        if self.tfm.character_coding_scheme == 'TeX math symbols':
            self.tfm.set_math_symbols_parameters(self.repeat(self.read_fix_word, 15))

        elif self.tfm.character_coding_scheme == 'TeX math extension':
            self.tfm.set_math_extension_parameters(self.repeat(self.read_fix_word, 6))

    ###############################################

    def process_char(self, c):
        
        width_index, height_index, depth_index, italic_index, tag, remainder = self.read_char_info(c)

        if width_ptr == 0: # unvalid char
            return

        width = self.read_fix_word(word_ptr(self.width_table_ptr, width_index))
        
        if height_ptr == 0:
            height = self.read_fix_word(word_ptr(self.height_table_ptr, height_index))
        else:
            height = 0

        if depth_ptr == 0:
            depth = self.read_fix_word(word_ptr(self.depth_table_ptr, depth_index))
        else:
            depth = 0

        if italic_ptr == 0:
            italic_correction = self.read_fix_word(word_ptr(self.italic_correction_table_ptr, italic_index))
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

    def read_char_info(self, c):
 
        index = c - self.smallest_character_code

        bytes = self.read_four_byte_numbers(word_ptr(self.character_info_ptr, index))

        width_ptr  = bytes[0]
        height_ptr = bytes[1] >> 4
        depth_ptr  = bytes[1] & 0xF
        italic_ptr = bytes[2] >> 6
        tag        = bytes[2] & 0x3
        remainder  = bytes[3]

        return width_ptr, height_ptr, depth_ptr, italic_ptr, tag, remainder

    ###############################################

    def read_extensible_recipe(self, index):
 
        return self.read_four_byte_numbers(word_ptr(self.extensible_character_table_ptr, index))

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
''' % (self.font_name,
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
