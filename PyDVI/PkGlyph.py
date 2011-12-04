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
#  - 17/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['PkGlyph']

#####################################################################################################

import math

import numpy as np

#####################################################################################################

from PyDVI.TeXUnit import *
from PyDVI.Tools.Logging import print_card

#####################################################################################################

class PkGlyph(object):

    ###############################################

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

    ###############################################

    def get_scaled_width(self, scale_factor):

        return int(self.tfm * scale_factor)

    ###############################################

    def get_nybble(self):

        '''
        Get the next nyblle
        '''

        byte = self.nybbles[self.nybble_index]

        if self.upper_nybble:
            nybble = byte >> 4
        else:
            nybble = byte & 0xF
            self.nybble_index += 1

        self.upper_nybble = not self.upper_nybble

        return nybble

    ###############################################

    def pk_packed_num(self):

        # cf. pktype.web from web2c

        i = self.get_nybble()

        if i == 0: # large run count
            # count the number of zeros / nybbles and read the first nybble
            while True: 
                j = self.get_nybble()
                i += 1
                if j != 0: break
            # decode the large run count
            while i > 0:
                j = j * 16 + self.get_nybble()
                i -= 1
            # scale it
            # next number is (13 - (dyn_f +1))*16 + 15 + (dyn_f +1) = (13 - dyn_f)*16 + dyn_f
            return j - 15 + (13 - self.dyn_f)*16 + self.dyn_f

        elif i <= self.dyn_f: # one-nybble packed number
            return i
        elif i < 14: # two-nybble packed number
            # next number is dyn_f +1
            # (nybble_1 - next_number)*16 + nybble_2 + next_number
            return (i - self.dyn_f - 1)*16 + self.get_nybble() + self.dyn_f + 1

        else: # repeat count
            if i == 14:
                # decode the repeat count
                self.repeat_count = self.pk_packed_num()
            else: # i == 15
                self.repeat_count = 1
            return self.pk_packed_num()

    ###############################################

    def raster_glyph(self, count_list=False):

        '''
        Unpack the glyph
        '''

        self.nybble_index = 0
        self.upper_nybble = True

        glyph_bitmap = self.glyph_bitmap = np.zeros((self.height, self.width), dtype = np.uint8)

        if self.dyn_f == 14: # get raster by bits

            i = 0
            bit_map = 0
            bit_weight = 0

            for y in xrange(self.height):
                for x in xrange(self.width):

                    bit_weight >> 1

                    if bit_weight == 0:
                        bit_map = self.nybbles[i]
                        i += 1
                        bit_weight = 0xFF

                    if bit_map & bit_weight:
                        glyph_bitmap[y,x] = 1

        else: # get packed raster

            packed_string = ''

            black_pixel = self.first_pixel_is_black
            transition = False
            self.repeat_count = 0
            x = 0
            y = 0

            while y < self.height:

                count = self.pk_packed_num()

                if count_list:

                    if transition:
                        packed_string += '[%u]' % (self.repeat_count)

                    if black_pixel:
                        packed_string += '%u' % (count)
                    else:
                        packed_string += '(%u)' % (count)

                while count > 0:

                    upper_x = x + count

                    if upper_x < self.width: # fill

                        if black_pixel:
                            glyph_bitmap[y,x:upper_x] = 1

                        count = 0
                        x = upper_x

                    else: # split count and repeat row if necessary

                        if black_pixel:
                            glyph_bitmap[y,x:] = 1

                        y_src = y
                        y += 1
                        for i in xrange(self.repeat_count):
                            glyph_bitmap[y,:] = glyph_bitmap[y_src,:]
                            y += 1
                        self.repeat_count = 0

                        count -= self.width - x
                        x = 0

                black_pixel = not black_pixel
                transition = not transition

        if count_list:
            print packed_string

    ###############################################

    def get_glyph_bitmap(self):

        if self.glyph_bitmap is None:
            self.raster_glyph()

        return self.glyph_bitmap

    ###############################################

    def print_glyph(self):

        glyph_bitmap = self.get_glyph_bitmap()

        axis = ' '*4 + '+' + '-'*self.width + '+'

        print axis

        for y in xrange(self.height):

            line = ''
            for x in xrange(self.width):
                if glyph_bitmap[y,x] == 1:
                    line += 'x'
                else:
                    line += ' '

            print '%3u |%s|' % (y, line)

        # print horizontal axis

        print axis

        number_of_digit = int(math.ceil(math.log10(self.width)))
        
        for i in xrange(number_of_digit, 0, -1):

            def digit(x):
                return str((x%10**i)/10**(i-1))
                
            line = ' '*5
            for x in xrange(self.width):
                line += digit(x)

            print line

    ###############################################

    def print_summary(self):

        width = self.tfm * self.pk_font.design_font_size

        print_card(''' Char %u
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
''' % (
                self.char_code,
                self.tfm, width, pt2mm(width),
                self.dm, self.dx, self.dy,
                self.height, self.width,
                self.horizontal_offset, self.vertical_offset))
        
#####################################################################################################
#
# End
#
#####################################################################################################

