####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
# - 11/12/2011 fabrice
#  - check bitmap glyph
#
####################################################################################################

""" This module provides functions to handle Packed Font Glyphs.
"""

####################################################################################################

__all__ = ['PkGlyph']

####################################################################################################

import math

import numpy as np

####################################################################################################

from PyDVI.TeXUnit import *
from PyDVI.Tools.Logging import print_card

####################################################################################################

class PkGlyph(object):

    """ This class contains the information stored in the Packed Font file for each glyph.  For
    efficiency, the run count list is lazy decoded.

    The glyph bitmap can be printed using the method :meth:`print_glyph`.  For example the output
    for the letter "A" of the font "cmr10" at 600 dpi is::

          0000000000111111111122222222223333333333444444444455555
          0123456789012345678901234567890123456789012345678901234
         +-------------------------------------------------------+
       0 |                          xxx                          |
       1 |                          xxx                          |
       2 |                          xxx                          |
       3 |                         xxxxx                         |
       4 |                         xxxxx                         |
       5 |                         xxxxx                         |
       6 |                        xxxxxxx                        |
       7 |                        xxxxxxx                        |
       8 |                        xxxxxxx                        |
       9 |                       xxxxxxxxx                       |
      10 |                       xxxxxxxxx                       |
      11 |                       xxxxxxxxx                       |
      12 |                      xx xxxxxxxx                      |
      13 |                      xx xxxxxxxx                      |
      14 |                     xxx xxxxxxxxx                     |
      15 |                     xx   xxxxxxxx                     |
      16 |                     xx   xxxxxxxx                     |
      17 |                    xxx   xxxxxxxxx                    |
      18 |                    xx     xxxxxxxx                    |
      19 |                    xx     xxxxxxxx                    |
      20 |                   xxx     xxxxxxxxx                   |
      21 |                   xx       xxxxxxxx                   |
      22 |                   xx       xxxxxxxx                   |
      23 |                  xxx       xxxxxxxxx                  |
      24 |                  xx         xxxxxxxx                  |
      25 |                  xx         xxxxxxxx                  |
      26 |                 xxx         xxxxxxxxx                 |
      27 |                 xx           xxxxxxxx                 |
      28 |                 xx           xxxxxxxx                 |
      29 |                xx            xxxxxxxxx                |
      30 |                xx             xxxxxxxx                |
      31 |                xx             xxxxxxxx                |
      32 |               xx              xxxxxxxxx               |
      33 |               xx               xxxxxxxx               |
      34 |               xx               xxxxxxxx               |
      35 |              xx                xxxxxxxxx              |
      36 |              xx                 xxxxxxxx              |
      37 |              xx                 xxxxxxxx              |
      38 |             xx                  xxxxxxxxx             |
      39 |             xxxxxxxxxxxxxxxxxxxxxxxxxxxxx             |
      40 |             xxxxxxxxxxxxxxxxxxxxxxxxxxxxx             |
      41 |            xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx            |
      42 |            xx                     xxxxxxxx            |
      43 |            xx                     xxxxxxxx            |
      44 |           xx                       xxxxxxxx           |
      45 |           xx                       xxxxxxxx           |
      46 |           xx                       xxxxxxxx           |
      47 |          xx                         xxxxxxxx          |
      48 |          xx                         xxxxxxxx          |
      49 |          xx                         xxxxxxxx          |
      50 |         xx                           xxxxxxxx         |
      51 |         xx                           xxxxxxxx         |
      52 |        xxx                           xxxxxxxx         |
      53 |        xxx                            xxxxxxxx        |
      54 |       xxxx                            xxxxxxxx        |
      55 |      xxxxxx                           xxxxxxxxx       |
      56 |    xxxxxxxxxx                       xxxxxxxxxxxx      |
      57 |xxxxxxxxxxxxxxxxx               xxxxxxxxxxxxxxxxxxxxxxx|
      58 |xxxxxxxxxxxxxxxxx               xxxxxxxxxxxxxxxxxxxxxxx|
      59 |xxxxxxxxxxxxxxxxx               xxxxxxxxxxxxxxxxxxxxxxx|
         +-------------------------------------------------------+
          0000000000111111111122222222223333333333444444444455555
          0123456789012345678901234567890123456789012345678901234
    
    Moreover the method :meth:`count_list` return a run count list string equivalent at the output of
    the command :command:`pktype`.  For example the output for the previous glyph is::
    
      (26)[2]3(51)[2]5(49)[2]7(47)[2]9(45)[1]2(1)8(43)3(1)9(42)[1]2(3)8(41)3(3)9 
      (40)[1]2(5)8(39)3(5)9(38)[1]2(7)8(37)3(7)9(36)[1]2(9)8(35)3(9)9(34)[1]2(11)8 
      (33)2(12)9(32)[1]2(13)8(31)2(14)9(30)[1]2(15)8(29)2(16)9(28)[1]2(17)8(27)2 
      (18)9(26)[1]29(25)31(24)[1]2(21)8(23)[2]2(23)8(21)[2]2(25)8(19)[1]2(27)8(17) 
      3(27)8(17)3(28)8(15)4(28)8(14)6(27)9(11)10(23)12(6)[2]17(15)23 

    """

    ##############################################

    def __init__(self,
                 pk_font,
                 char_code,
                 tfm, dm, dx, dy,
                 height, width,
                 horizontal_offset, vertical_offset,
                 nybbles, dyn_f, first_pixel_is_black):

        self.pk_font = pk_font

        self.char_code = char_code
        self.tfm, self.dm, self.dx, self.dy = tfm, dm, dx, dy
        self.height, self.width = height, width
        self.horizontal_offset, self.vertical_offset = horizontal_offset, vertical_offset
        self.nybbles, self.dyn_f, self.first_pixel_is_black = nybbles, dyn_f, first_pixel_is_black

        self.glyph_bitmap = None

        self.pk_font.register_glyph(self)

    ##############################################

    def _init_packed_number_decoder(self):

        """ Init the packed number decoder. """

        self._nybble_index = 0
        self._upper_nybble = True
        self._repeat_row_count = 0

    ##############################################

    def _next_nybble(self):

        """ Return the next nybble from the byte array.
        """

        byte = self.nybbles[self._nybble_index]

        if self._upper_nybble:
            nybble = byte >> 4
        else:
            nybble = byte & 0xF
            self._nybble_index += 1

        self._upper_nybble = not self._upper_nybble

        return nybble

    ##############################################

    def _next_packed_number(self):

        """ Decode a packed number from the byte array.
        """

        i = self._next_nybble()

        if i == 0: # large run count
            # count the number of zeros, coding the number of nybbles and read the first nybble
            while True: 
                j = self._next_nybble()
                i += 1
                if j != 0: break
            # then decode the large run count
            while i > 0:
                j = j*16 + self._next_nybble()
                i -= 1
            # and finally scale it
            #   for one zero: j = nybble_1*16 + nybble_2
            #   min(j) = 1*16 + 0 = 16
            #   thus j -16 + upper_2_nybble +1
            return j - 15 + (13 - self.dyn_f)*16 + self.dyn_f

        elif i <= self.dyn_f: # one-nybble packed number: [1, dyn_f]
            return i
        elif i < 14: # two-nybble packed number: [dyn_f +1, (13 - dyn_f)*16 + dyn_f]
            next_number = self.dyn_f +1
            # packed number = (nybble_1 - next_number)*16 + nybble_2 + next_number
            # upper number = (13 - (dyn_f +1))*16 + 15 + (dyn_f +1) = (13 - dyn_f)*16 + dyn_f
            return (i - next_number)*16 + self._next_nybble() + next_number

        else: # repeat row count
            if i == 14:
                # decode the repeat row count
                self._repeat_row_count = self._next_packed_number()
            else: # i == 15
                self._repeat_row_count = 1
            return self._next_packed_number()

    ##############################################

    def _decode_bitmap_glyph(self):

        """ Decode a bitmap glyph. """

        size = self.height * self.width
        glyph_bitmap = self.glyph_bitmap = np.zeros(size, dtype=np.bool)

        i = 0
        for byte in self.nybbles:
            mask = 128
            for j in xrange(8):
                glyph_bitmap[i] = bool(byte & mask)
                mask >>= 1
                i += 1
            if i == size:
                break
        glyph_bitmap.shape = self.height, self.width

    ##############################################

    def _decode_packed_glyph(self):

        """ Decode a packed glyph. """

        # Fixme: try linear approach
        #  current i and row = int(i / width)

        # row 0 corresponds to the glyph's top

        glyph_bitmap = self.glyph_bitmap = np.zeros((self.height, self.width), dtype=np.bool)

        self._init_packed_number_decoder()
        black_pixel = self.first_pixel_is_black
        x = 0
        y = 0

        while y < self.height:
            count = self._next_packed_number()
            while count > 0:
                upper_x = x + count
                # if upper_x is in the actual row then fill count pixels
                if upper_x < self.width:
                    if black_pixel:
                        glyph_bitmap[y, x:upper_x] = True
                    count = 0
                    x = upper_x
                # else split and repeat row if necessary
                else: 
                    if black_pixel: # fill the current row
                        glyph_bitmap[y, x:] = True
                    y_src = y
                    y += 1 # goto next row
                    #!# if self._repeat_row_count:
                    # copy repeat_row_count times the current row and increment y
                    for i in xrange(self._repeat_row_count):
                        glyph_bitmap[y,:] = glyph_bitmap[y_src,:]
                        y += 1
                    self._repeat_row_count = 0
                    count -= self.width - x
                    x = 0
            # flip state
            black_pixel = not black_pixel

    ##############################################

    def _decode_glyph(self):

        """ Decode the glyph. """
        
        if self.is_bitmap():
            self._decode_bitmap_glyph()
        else:
            self._decode_packed_glyph()

    ##############################################

    def count_list(self):

        """ Return the count list as :command:`pktype`. """

        # The count list start from the top-left corner of the glyph's bounding box and follows the
        # top-down and left-right raster order.

        if self.is_bitmap():
            return 'bitmap glyph'

        count_string = ''
        self._init_packed_number_decoder()
        black_pixel = self.first_pixel_is_black
        transition = False
        i = 0
        size = self.height * self.width
        while i < size:
            count = self._next_packed_number()
            i += count
            if transition and self._repeat_row_count:
                i += self.width * self._repeat_row_count
                count_string += '[%u]' % (self._repeat_row_count)
                self._repeat_row_count = 0
            if black_pixel:
                count_string += '%u' % (count)
            else:
                count_string += '(%u)' % (count)
            black_pixel = not black_pixel
            transition = not transition

        return count_string

    ##############################################

    def is_bitmap(self):

        """ Return :obj:`True` is the glyph use the bitmap format. """

        return self.dyn_f == 14

    ##############################################

    def get_scaled_width(self, scale_factor):

        """ Return the width scaled by *scale_factor*. """

        return int(self.tfm * scale_factor)

    ##############################################

    def get_glyph_bitmap(self):

        """ Return the glyph bitmap as a Numpy array. """

        if self.glyph_bitmap is None:
            self._decode_glyph()

        return self.glyph_bitmap

    ##############################################

    def print_glyph(self):

        """ Print the glyph. """

        glyph_bitmap = self.get_glyph_bitmap()

        axis = ' '*4 + '+' + '-'*self.width + '+'

        def print_label_axis():
            number_of_digit = int(math.ceil(math.log10(self.width)))
            for i in xrange(number_of_digit, 0, -1):
                line = ' '*5
                for x in xrange(self.width):
                    line += str((x%10**i)/10**(i-1))
                print line

        print_label_axis()
        print axis

        for y in xrange(self.height):
            line = ''
            for x in xrange(self.width):
                if glyph_bitmap[y,x]:
                    line += 'x'
                else:
                    line += ' '
            print '%3u |%s|' % (y, line)

        print axis
        print_label_axis()

    ##############################################

    def print_summary(self):

        string_format = ''' Char %u
 - TFM width: %.3f * design size
              %.1f pt
              %.1f mm
 - dm:                %3u px
 - dx:                %3u px
 - dy:                %3u px
 - Height:            %3u px
 - Width:             %3u px
 - Horizontal Offset: %3u px
 - Vertical Offset:   %3u px
'''
        width = self.get_scaled_width(self.pk_font.design_font_size)

        print_card(string_format % (
                self.char_code,
                self.tfm, width, pt2mm(width),
                self.dm, self.dx, self.dy,
                self.height, self.width,
                self.horizontal_offset, self.vertical_offset))
        
####################################################################################################
#
# End
#
####################################################################################################

