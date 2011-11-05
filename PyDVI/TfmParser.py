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
# - 01/11/2011 Fabrice
#   - check parse definition
#
#####################################################################################################

"""
This module handles TFM files.

TFM file format in descriped in :file:`tftopl` web file.
"""

#####################################################################################################

__all__ = ['TfmParser']

#####################################################################################################

from EnumFactory import EnumFactory
from Stream import *
from Tfm import *

#####################################################################################################

NO_TAG, LIG_TAG, LIST_TAG, EXT_TAG = range(4)

KERN_OPCODE = 128

#####################################################################################################

#: Defines the tables present in a TFM file.
tables = EnumFactory('TableEnums', 
                     ('header',
                      'character_info',
                      'width',
                      'height',
                      'depth',
                      'italic_correction',
                      'lig_kern',
                      'kern',
                      'extensible_character',
                      'font_parameter',
                      ))

#####################################################################################################

def repeat(func, count):

    """ Call *func* *count* times. """

    return [func() for i in xrange(count)]

#####################################################################################################

class TfmParser(object):

    """
    This class parse a TFM_file.

    """

    ###############################################

    @staticmethod
    def word_ptr(base, index):

        return base + 4*index

    ###############################################

    def seek_to_table(self, table):

        self.stream.seek(self.table_pointers[table])

    ###############################################

    def position_in_table(self, table, index):

        return self.word_ptr(self.table_pointers[table], index)

    ###############################################

    def read_fix_word_in_table(self, table, index):

        return self.stream.read_fix_word(self.position_in_table(table, index))

    ###############################################

    def read_four_byte_numbers_in_table(self, table, index):

        return self.stream.read_four_byte_numbers(self.position_in_table(table, index))

    ###############################################

    def parse(self, font_name, filename):

        """ Parse the :file:`filename`.
        """

        # Fixme: API ok?

        self.font_name = font_name
        self.filename = filename

        self.stream = FileStream(filename)

        self._read_lengths()
        self.read_header()
        self.read_font_parameters()
        self.read_lig_kern_programs()
        
        for c in xrange(self.smallest_character_code, self.largest_character_code +1):
            self.process_char(c)
         
        self.stream = None

        return self.tfm

    ###############################################

    def _read_lengths(self):
        
        """
        The fist 24 bytes (6 words) of a TFM file contain twelve 16-bit integers that give the
        lengths of the various subsequent portions of the file. These twelve integers are, in order:

          * lf = length of the entire file, in words;
          * lh = length of the header data, in words;
          * bc = smallest character code in the font;
          * ec = largest character code in the font;
          * nw = number of words in the width table;
          * nh = number of words in the height table;
          * nd = number of words in the depth table;
          * ni = number of words in the italic correction table;
          * nl = number of words in the lig/kern table;
          * nk = number of words in the kern table;
          * ne = number of words in the extensible character table;
          * np = number of font parameter words.

        They are all nonnegative and less than 2**15. We must have bc - 1 <= ec <= 255, ne <= 256,
        and lf = 6 + lh + (ec - bc + 1) + nw + nh + nd + ni + nl + nk + ne + np.

        Note that a font may contain as many as 256 characters (if bc = 0 and ec = 255), and as few
        as 0 characters (if bc = ec + 1).

        The header must contain at least two words, and for TFM files to be used with Xerox printing
        software it must contain at least 18 words.
        """

        stream = self.stream
        stream.seek(0)

        # Read and set table lengths

        self.table_lengths = [None]*len(tables)

        (self.entire_file_length,
         header_length,
         self.smallest_character_code,
         self.largest_character_code) = repeat(stream.read_unsigned_byte2, 4)

        header_data_length_min = 18 # words
        self.table_lengths[tables.header] = max(header_data_length_min, header_length)
        
        self.number_of_chars = self.largest_character_code - self.smallest_character_code +1
        self.table_lengths[tables.character_info] = self.number_of_chars

        # read the last lengths
        for i in xrange(tables.width, len(tables)):
            self.table_lengths[i] = stream.read_unsigned_byte2()

        # Compute table pointers

        self.table_pointers = [None]*len(tables)

        # The header starts at 24 bytes
        self.table_pointers[tables.header] = 24

        for table in xrange(tables.header, tables.font_parameter):
            self.table_pointers[table+1] = self.position_in_table(table, self.table_lengths[table])

        length = self.position_in_table(tables.font_parameter, self.table_lengths[tables.font_parameter])
        if length != self.word_ptr(0, self.entire_file_length):
            raise NameError('Bad TFM file')

    ###############################################

    def read_header(self):
        
        stream = self.stream

        character_coding_scheme_length = 40
        family_length = 10

        self.seek_to_table(tables.header)

        checksum = stream.read_unsigned_byte4()
        design_font_size = stream.read_fix_word()
        
        character_info_table_position = self.table_pointers[tables.character_info]

        position = stream.tell()

        if position < character_info_table_position:
            character_coding_scheme = stream.read_bcpl()
        else:
            character_coding_scheme = None

        position += character_coding_scheme_length

        if position < character_info_table_position:
            family = stream.read_bcpl(position)
        else:
            family = None

        position += family_length

        if position < character_info_table_position:
            seven_bit_safe_flag = stream.read_unsigned_byte4(position)
            # Fixme: complete

        self.tfm = Tfm(self.font_name,
                       self.filename,
                       self.smallest_character_code,
                       self.largest_character_code,
                       checksum,
                       design_font_size,
                       character_coding_scheme,
                       family)

    ###############################################

    def read_font_parameters(self):
                 
        stream = self.stream

        self.seek_to_table(tables.font_parameter)
 
        # print 'read_font_parameters', self.tfm.character_coding_scheme, self.table_lengths[tables.font_parameter]

        if self.tfm.character_coding_scheme == 'TeX math italic':
            pass
        else:
            self.tfm.set_font_parameters(repeat(stream.read_fix_word, 7))

        if self.tfm.character_coding_scheme == 'TeX math symbols':
            self.tfm.set_math_symbols_parameters(repeat(stream.read_fix_word, 15))

        elif self.tfm.character_coding_scheme == 'TeX math extension':
            self.tfm.set_math_extension_parameters(repeat(stream.read_fix_word, 6))

    ###############################################

    def read_lig_kern_programs(self):

        # Fixme: complete special cases

        # Read very first instruction of the table

        (first_skip_byte,
         next_char,
         op_byte,
         remainder) = self.read_four_byte_numbers_in_table(tables.lig_kern, 0)
        
        if first_skip_byte == 255:
            right_boundary_char = next_char
            raise NameError('Font has right boundary char')

        # Read very last instruction of the table

        (last_skip_byte,
         next_char,
         op_byte,
         remainder) = self.read_four_byte_numbers_in_table(tables.lig_kern,
                                                           self.table_lengths[tables.lig_kern] -1)
        
        if last_skip_byte == 255:
            left_boundary_char_program_index = 256*op_byte + remainder
            raise NameError('Font has left boundary char program')

        # Read the instructions

        first_instruction = True

        for i in xrange(self.table_lengths[tables.lig_kern]):
        
            (skip_byte,
             next_char,
             op_byte,
             remainder) = self.read_four_byte_numbers_in_table(tables.lig_kern, i)
        
            if first_instruction and skip_byte > 128:

                print 'Large lig/kern table'

                large_index = 256*op_byte + remainder

                (skip_byte,
                 next_char,
                 op_byte,
                 remainder) = self.read_four_byte_numbers_in_table(tables.lig_kern, large_index)

            stop = skip_byte >= 128

            if op_byte >= KERN_OPCODE:
        
                kern_index = 256*(op_byte - KERN_OPCODE) + remainder
                kern = self.read_fix_word_in_table(tables.kern, kern_index)
        
                TfmKern(self.tfm, i, stop, next_char, kern)
        
            else:
        
                number_of_chars_to_pass_over = op_byte >> 2
                current_char_is_deleted = (op_byte & 0x02) == 0
                next_char_is_deleted    = (op_byte & 0x01) == 0
        
                ligature_char_code = remainder
        
                TfmLigature(self.tfm,
                            i,
                            stop,
                            next_char,
                            ligature_char_code,
                            number_of_chars_to_pass_over,
                            current_char_is_deleted,
                            next_char_is_deleted)

            first_instruction = stop == True

    ###############################################

    def process_char(self, c):
        
        width_index, height_index, depth_index, italic_index, tag, remainder = self.read_char_info(c)

        if width_index == 0: # unvalid char
            return

        width = self.read_fix_word_in_table(tables.width, width_index)
        
        if height_index != 0:
            height = self.read_fix_word_in_table(tables.height, height_index)
        else:
            height = 0

        if depth_index != 0:
            depth = self.read_fix_word_in_table(tables.depth, depth_index)
        else:
            depth = 0

        if italic_index != 0:
            italic_correction = self.read_fix_word_in_table(tables.italic_correction, italic_index)
        else:
            italic_correction = 0

        lig_kern_program_index = None
        next_larger_char = None
        extensible_recipe = None

        if tag == LIG_TAG:
            lig_kern_program_index = remainder
            
        elif tag == LIST_TAG:
            next_larger_char = remainder

        elif tag == EXT_TAG:
            extensible_recipe = self.read_extensible_recipe(remainder)

        if extensible_recipe is not None:
            TfmExtensibleChar(self.tfm,
                              c,
                              width,
                              height,
                              depth,
                              italic_correction,
                              extensible_recipe,
                              lig_kern_program_index,
                              next_larger_char)

        else:
            TfmChar(self.tfm,
                    c,
                    width,
                    height,
                    depth,
                    italic_correction,
                    lig_kern_program_index,
                    next_larger_char)

    ###############################################

    def read_char_info(self, c):
 
        index = c - self.smallest_character_code

        bytes = self.read_four_byte_numbers_in_table(tables.character_info, index)

        width_index  = bytes[0]
        height_index = bytes[1] >> 4
        depth_index  = bytes[1] & 0xF
        italic_index = bytes[2] >> 6
        tag          = bytes[2] & 0x3
        remainder    = bytes[3]

        return width_index, height_index, depth_index, italic_index, tag, remainder

    ###############################################

    def read_extensible_recipe(self, index):
 
        return self.read_four_byte_numbers_in_table(tables.extensible_character, index)

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
       self.table_lengths[tables.header],
       self.smallest_character_code,
       self.largest_character_code,
       self.table_lengths[tables.width],
       self.table_lengths[tables.height],
       self.table_lengths[tables.depth],
       self.table_lengths[tables.italic_correction],
       self.table_lengths[tables.lig_kern],
       self.table_lengths[tables.kern],
       self.table_lengths[tables.extensible_character],
       self.table_lengths[tables.font_parameter],
       )

#####################################################################################################
#
# End
#
#####################################################################################################
