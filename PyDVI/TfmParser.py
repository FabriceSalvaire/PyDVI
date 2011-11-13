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
This module handles TeX Font Metric files.

A TFM file gives the metrics for a TeX font. It uses the ".tfm" extension.

The TFM file format in descriped in the :file:`tftopl` web file.

The information in a TFM file appears in a sequence of 8-bit bytes. Since the number of bytes is
always a multiple of 4, we could also regard the file as a sequence of 32-bit words. Note that the
bytes are considered to be unsigned numbers.
"""

#####################################################################################################

__all__ = ['TfmParser']

#####################################################################################################

from PyDVI.Tfm import *
from PyDVI.Tools.EnumFactory import EnumFactory
from PyDVI.Tools.Stream import *

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
    This class parse a TFM file.
    """

    ###############################################

    @staticmethod
    def word_ptr(base, index):

        """ Compute the pointer to the word element index *index* from the base *base*.  A word
        element has a size of 32-bit.

          ``prt = base + 4*index``
        """

        return base + 4*index

    ###############################################

    def seek_to_table(self, table):

        """ Seek to the table *table*.
        """

        self.stream.seek(self.table_pointers[table])

    ###############################################

    def _position_in_table(self, table, index):

        """ Return a pointer to the word element at *index* in the table *table*.
        """

        return self.word_ptr(self.table_pointers[table], index)

    ###############################################

    def read_fix_word_in_table(self, table, index):

        return self.stream.read_fix_word(self._position_in_table(table, index))

    ###############################################

    def read_four_byte_numbers_in_table(self, table, index):

        return self.stream.read_four_byte_numbers(self._position_in_table(table, index))

    ###############################################

    # Fixme: API ok?

    def parse(self, font_name, filename):

        """ Parse the TFM :file:`filename` for the font *font_name*.
        """

        self.font_name = font_name
        self.filename = filename

        self.stream = FileStream(filename)

        self._read_lengths()
        self._read_header()
        self._read_font_parameters()
        self._read_lig_kern_programs()
   
        # Read the character information table
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

        They are all nonnegative and less than 2**15. We must have ``bc - 1 <= ec <= 255``, ``ne <=
        256``, and
     
          ``lf = 6 + lh + (ec - bc + 1) + nw + nh + nd + ni + nl + nk + ne + np``.

        Note that a font may contain as many as 256 characters (if ``bc = 0`` and ``ec = 255``), and
        as few as 0 characters (if ``bc = ec + 1``).

        The rest of the TFM file may be regarded as a sequence of ten data arrays having the
        informal specification:

          ========== ===================== ====================
          header     array [0  ... lh - 1] of stuff
          char info  array [bc ... ec    ] of char info word
          width      array [0  ... nw - 1] of fix word
          height     array [0  ... nh - 1] of fix word
          depth      array [0  ... nd - 1] of fix word
          italic     array [0  ... ni - 1] of fix word
          lig kern   array [0  ... nl - 1] of lig kern command
          kern       array [0  ... nk - 1] of fix word
          exten      array [0  ... ne - 1] of extensible recipe
          param      array [1  ... np    ] of fix word
          ========== ===================== ====================
        """

        stream = self.stream
        stream.seek(0)

        ###########
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

        ###########
        # Compute table pointers
        self.table_pointers = [None]*len(tables)

        # The header starts at 24 bytes
        self.table_pointers[tables.header] = 24

        for table in xrange(tables.header, tables.font_parameter):
            self.table_pointers[table+1] = self._position_in_table(table, self.table_lengths[table])

        ###########
        # Sanity check
        length = self._position_in_table(tables.font_parameter, self.table_lengths[tables.font_parameter])
        if length != self.word_ptr(0, self.entire_file_length):
            raise NameError('Bad TFM file')

    ###############################################

    def _read_header(self):

        """ The first data array is a block of header information, which contains general facts
        about the font.  The header must contain at least two words, and for TFM files to be used
        with Xerox printing software it must contain at least 18 words, allocated as described
        below.

        header [0] is a 32-bit check sum that TEX will copy into the DVI output file whenever it
        uses the font.  Later on when the DVI file is printed, possibly on another computer, the
        actual font that gets used is supposed to have a check sum that agrees with the one in the
        TFM file used by TEX.  In this way, users will be warned about potential incompatibilities.
        (However, if the check sum is zero in either the font file or the TFM file, no check is
        made.)  The actual relation between this check sum and the rest of the TFM file is not
        important; the check sum is simply an identification number with the property that
        incompatible fonts almost always have distinct check sums.

        header [1] is a fix word containing the design size of the font, in units of TEX points
        (7227 TEX points = 254 cm).  This number must be at least 1.0; it is fairly arbitrary, but
        usually the design size is 10.0 for a "10 point" font, i.e., a font that was designed to
        look best at a 10-point size, whatever that really means.  When a TEX user asks for a font
        `at delta pt', the effect is to override the design size and replace it by delta, and to
        multiply the x and y coordinates of the points in the font image by a factor of delta
        divided by the design size.  All other dimensions in the TFM file are fix word numbers in
        design-size units.  Thus, for example, the value of param[6], one em or \quad, is often the
        fix word value 2**20 = 1.0, since many fonts have a design size equal to one em.  The other
        dimensions must be less than 16 design-size units in absolute value; thus, header[1] and
        param[1] are the only fix word entries in the whole TFM file whose first byte might be
        something besides 0 or 255.
        
        header [2 ... 11], if present, contains 40 bytes that identify the character coding scheme.
        The first byte, which must be between 0 and 39, is the number of subsequent ASCII bytes
        actually relevant in this string, which is intended to specify what character-code-to-symbol
        convention is present in the font.  Examples are ASCII for standard ASCII, TeX text for
        fonts like cmr10 and cmti9, TeX math extension for cmex10, XEROX text for Xerox fonts,
        GRAPHIC for special-purpose non- alphabetic fonts, UNSPECIFIED for the default case when
        there is no information.  Parentheses should not appear in this name.  (Such a string is
        said to be in BCPL format.)

        header [12 ... 16], if present, contains 20 bytes that name the font family (e.g., CMR or
        HELVETICA), in BCPL format.  This field is also known as the "font identifier."

        header [17], if present, contains a first byte called the *seven_bit_safe_flag*, then two
        bytes that are ignored, and a fourth byte called the *face*.  If the value of the fourth
        byte is less than 18, it has the following interpretation as a "weight, slope, and
        expansion": Add 0 or 2 or 4 (for medium or bold or light) to 0 or 1 (for roman or italic) to
        0 or 6 or 12 (for regular or condensed or extended).  For example, 13 is 0+1+12, so it
        represents medium italic extended.  A three-letter code (e.g., MIE) can be used for such
        face data.

        header [18 ... whatever] might also be present; the individual words are simply called
        header [18], header [19], etc., at the moment.
        """
        
        stream = self.stream

        self.seek_to_table(tables.header)

        # Read header[0 ... 1]
        checksum = stream.read_unsigned_byte4()
        design_font_size = stream.read_fix_word()
        
        # Read header[2 ... 11] if there
        character_info_table_position = self.table_pointers[tables.character_info]
        position = stream.tell()
        if position < character_info_table_position:
            character_coding_scheme = stream.read_bcpl()
        else:
            character_coding_scheme = None

        # Read header[12 ... 16] if there
        character_coding_scheme_length = 40 # bytes (11 - 2 + 1) * 4 = 10 * 4 
        position += character_coding_scheme_length
        if position < character_info_table_position:
            family = stream.read_bcpl(position)
        else:
            family = None

        # Read header[12 ... 16] if there
        family_length = 20 # bytes (16 - 12 +1) * 4 = 5 * 4 
        position += family_length
        if position < character_info_table_position:
            seven_bit_safe_flag = stream.read_unsigned_byte(position)
            stream.read_unsigned_byte2()
            face = stream.read_unsigned_byte()
            # Fixme: complete

        # don't read header [18 ... whatever]

        self.tfm = Tfm(self.font_name,
                       self.filename,
                       self.smallest_character_code,
                       self.largest_character_code,
                       checksum,
                       design_font_size,
                       character_coding_scheme,
                       family)

    ###############################################

    def _read_font_parameters(self):

        """ The final portion of a TFM fie is the param array, which is another sequence of fix word
        values.

          * param[1] = *slant* is the amount of italic slant, which is used to help position accents.
            For example, slant = .25 means that when you go up one unit, you also go .25 units to
            the right.  The slant is a pure number; it's the only fix word other than the design
            size itself that is not scaled by the design size.
          * param[2] = *space* is the normal spacing between words in text. Note that character " " in
            the font need not have anything to do with blank spaces.
          * param[3] = *space_stretch* is the amount of glue stretching between words.
          * param[4] = *space_shrink* is the amount of glue shrinking between words.
          * param[5] = *x_height* is the height of letters for which accents don't have to be raised
            or lowered.
          * param[6] = *quad* is the size of one em in the font.
          * param[7] = *extra_space* is the amount added to param[2] at the ends of sentences.

        When the character coding scheme is *TeX math symbols*, the font is supposed to have 15
        additional parameters called *num1*, *num2*, *num3*, *denom1*, *denom2*, *sup1*, *sup2*,
        *sup3*, *sub1*, *sub2*, *supdrop*, *subdrop*, *delim1*, *delim2*, and *axis_height*,
        respectively.  When the character coding scheme is *TeX math extension*, the font is
        supposed to have six additional parameters called *defaul_rule_thickness* and
        *big_op_spacing1* through *big_op_spacing5*.
        """
        
        stream = self.stream

        self.seek_to_table(tables.font_parameter)
 
        if self.tfm.character_coding_scheme == 'TeX math italic':
            # undocumented in tftopl web
            pass
        else:
            # Read the seven fix word parameters
            self.tfm.set_font_parameters(repeat(stream.read_fix_word, 7))

        if self.tfm.character_coding_scheme == 'TeX math symbols':
            # Read the additional 15 fix word parameters
            self.tfm.set_math_symbols_parameters(repeat(stream.read_fix_word, 15))
        elif self.tfm.character_coding_scheme == 'TeX math extension':
            # Read the additional 6 fix word parameters
            self.tfm.set_math_extension_parameters(repeat(stream.read_fix_word, 6))

    ###############################################

    def _read_lig_kern_programs(self):

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
        
        """ Next comes the char info array, which contains one char info word per character.  Each
        char info word contains six fields packed into four bytes as follows.

          * first byte: *width_index* (8 bits)
          * second byte: *height_index* (4 bits) times 16, plus depth index (4 bits)
          * third byte: *italic_index* (6 bits) times 4, plus tag (2 bits)
          * fourth byte: *remainder* (8 bits)

        The actual width of a character is ``width[width_index]``, in design-size units; this is a
        device for compressing information, since many characters have the same width.  Since it is
        quite common for many characters to have the same height, depth, or italic correction, the
        TFM format imposes a limit of 16 different heights, 16 different depths, and 64 different
        italic corrections.

        Incidentally, the relation ``width [0] = height [0] = depth [0] = italic [0] = 0`` should
        always hold, so that an index of zero implies a value of zero.  The width index should never
        be zero unless the character does not exist in the font, since a character is valid if and
        only if it lies between ``bc`` and ``ec`` and has a nonzero width index.

        The tag field in a char info word has four values that explain how to interpret the remainder field.

          * ``tag = 0`` (*no_tag*) means that remainder is unused.

          * ``tag = 1`` (*lig_tag*) means that this character has a ligature/kerning program
            starting at ``lig_kern[remainder]``.

          * ``tag = 2`` (*list_tag*) means that this character is part of a chain of characters of
            ascending sizes, and not the largest in the chain.  The remainder field gives the
            character code of the next larger character.

          * ``tag = 3`` (*ext_tag*) means that this character code represents an extensible
            character, i.e., a character that is built up of smaller pieces so that it can be made
            arbitrarily large.  The pieces are specified in ``exten[remainder]``.

          * ``no_tag = 0`` vanilla character
          * ``lig_tag = 1`` character has a ligature/kerning program
          * ``list_tag = 2`` character has a successor in a charlist
          * ``ext_tag = 3`` character is extensible
        """

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
