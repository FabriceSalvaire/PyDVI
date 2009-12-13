#####################################################################################################

import numpy as np

#####################################################################################################

from TeXUnit import sp2pt, sp2mm

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

    def get_nybble(self):

        if self.upper_nybble is True:
            nybble = ord(self.nybbles[self.nybble_index]) >> 4
        else:
            nybble = ord(self.nybbles[self.nybble_index]) & 0xF
            self.nybble_index += 1

        self.upper_nybble = not self.upper_nybble

        return nybble

    ###############################################

    def pk_packed_num(self):

        # cf. pktype.web from web2c

        i = self.get_nybble()

        if i == 0:
            while True:
                j  = self.get_nybble()
                i += 1
                if j != 0: break
            while i > 0:
                j  = j * 16 + self.get_nybble()
                i -= 1
            return j - 15 + (13 - self.dyn_f) * 16 + self.dyn_f

        elif i <= self.dyn_f:
            return i

        elif i < 14:
            return (i - self.dyn_f - 1) * 16 + self.get_nybble() + self.dyn_f + 1

        else:
            if i == 14:
                self.repeat_count = self.pk_packed_num()
            else :
                self.repeat_count = 1;
            return self.pk_packed_num()

    ###############################################

    def raster_glyph(self, count_list = False):

        '''
        Unpack the glyph
        '''

        self.nybble_index = 0
        self.upper_nybble = True

        glyph_bitmap = self.glyph_bitmap = np.zeros((self.height, self.width))

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

                if count_list is True:

                    if transition is True:
                        packed_string += '[%u]' % (self.repeat_count)

                    if black_pixel is True:
                        packed_string += '%u' % (count)
                    else:
                        packed_string += '(%u)' % (count)

                while count > 0:

                    upper_x = x + count

                    if upper_x < self.width: # fill

                        if black_pixel is True:
                            glyph_bitmap[y,x:upper_x] = 1

                        count = 0
                        x = upper_x

                    else: # split count and repeat row if necessary

                        if black_pixel is True:
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

        if count_list is True:
            print packed_string

    ###############################################

    def get_glyph_bitmap(self):

        if self.glyph_bitmap is None:
            self.raster_glyph()

        return self.glyph_bitmap

    ###############################################

    def print_glyph(self):

        glyph_bitmap = self.get_glyph_bitmap()

        for y in xrange(self.height):
            line = ''
            for x in xrange(self.width):
                if glyph_bitmap[y,x] == 1:
                    line += 'x'
                else:
                    line += ' '
            print '%3u |%s|' % (y, line)


    ###############################################

    def print_summary(self):

        print '''
Char %u
 - TFM width: %u sp %.1f pt %.1f mm
 - dm: %u px
 - dx: %u px
 - dy: %u px
 - Height: %u px
 - Width: %u px
 - Horizontal Offset: %u px
 - Vertical Offset: %u px
''' % (self.char_code,
       self.tfm, sp2pt(self.tfm), sp2mm(self.tfm),
       self.dm, self.dx, self.dy,
       self.height, self.width,
       self.horizontal_offset, self.vertical_offset)
        
#####################################################################################################
#
# End
#
#####################################################################################################

