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
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['Type1Font']

#####################################################################################################

import string

import ft2

#####################################################################################################

from Font import *
from Logging import *

#####################################################################################################

def test_bit(flags, mask):
    return flags & mask == 1

# 1/64th of pixels

def convert_26_6(x):
    return float(x)/2**6

# 1/65536th of pixels

def convert_16_16(x):
    return float(x)/2**16

#####################################################################################################

class FtGlyph(object):

    ###############################################

    def __init__(self, font, glyph_index, size, resolution):

        self.font = font
        self.glyph_index = glyph_index
        self.size = size
        self.resolution = resolution

        face = self.font.face

        size *= 64
        face.setCharSize(size, size, resolution, resolution)

        self.glyph = ft2.Glyph(face, glyph_index, 0)

        # print 'Char Box:', map(convert_26_6, self.glyph.getCBox(ft2.ft_glyph_bbox_subpixels))
        # print 'Advance:', map(convert_16_16, self.glyph.advance)

        posx, posy = 0, 0
        self.glyph_bitmap = ft2.Bitmap(self.glyph, ft2.FT_RENDER_MODE_NORMAL, posx, posy)

        # bitmap = np.fromstring(glyph_bitmap.bitmap, dtype=np.uint8)
        # bitmap.shape = glyph_bitmap.rows, glyph_bitmap.width
        # print 'Bitmap shape:', bitmap.shape

        # print 'Left:', self.glyph_bitmap.left
        # print 'Top:', self.glyph_bitmap.top
        # print 'Number of grays:', self.glyph_bitmap.num_grays
        # print 'Pixel Mode:', self.glyph_bitmap.pixel_mode
        # print 'Palette Mode:', self.glyph_bitmap.palette_mode

#####################################################################################################

class Type1Font(Font):

    font_type_string = 'PostScript Type1 Font'
    extension = 'pfb'

    ###############################################

    def __init__(self, font_manager, id, name):

        super(Type1Font, self).__init__(font_manager, id, name)

        self.__load_font()

        if self.set_unicode_char_map() is False:
            raise NameError("Font %s doesn't have an Unicode char map" % (self.name))

        self.glyphs = {}

    ###############################################

    def __load_font(self):

        try:
            self.face = ft2.Face(self.font_manager.freetype_library, self.filename, 0) # Fixme: index 0?
        except:
            raise NameError("Freetype can't open file %s" % (self.filename))

    ###############################################

    def get_char_map(self, i):

        return ft2.CharMap(self.face, i)

    ###############################################

    def set_unicode_char_map(self):

        for i in range(self.face.num_charmaps):
            
            charmap = self.get_char_map(i)
            
            if charmap.encoding_as_string == 'unic':
                self.face.setCharMap(charmap)
                return True

        return False

    ###############################################

    def hash_glyph(self, glyph_index, size, resolution):

        return hex(glyph_index)[2:] + hex(size)[1:] + hex(resolution)[1:]

    ###############################################

    def get_glyph(self, glyph_index, size, resolution):

        glyph_hash_key = self.hash_glyph(glyph_index, size, resolution)

        if self.glyphs.has_key(glyph_hash_key) is True:
            glyph = self.glyphs[glyph_hash_key]
        else:
            glyph = self.glyphs[glyph_hash_key] = FtGlyph(self, glyph_index, size, resolution)

        return glyph

    ###############################################

    def print_summary(self):

        face = self.face

        print_card(self.print_header() + 
                    '''
Postscript Name: %s
Family Name: %s
Style Name: %s
Number of Glyphs: %u
Flags: %s
Units per EM: %u
Bold: %s
Italic: %s
Scalable: %s
Char Maps: %s''' % (
                face.getPostscriptName(),
                face.family_name,
                face.style_name,
                face.num_glyphs,
                hex(face.style_flags),
                face.units_per_EM,
                test_bit(face.style_flags, ft2.FT_STYLE_FLAG_BOLD),
                test_bit(face.style_flags, ft2.FT_STYLE_FLAG_ITALIC),
                test_bit(face.style_flags, ft2.FT_FACE_FLAG_SCALABLE),
                map(lambda i: self.get_char_map(i).encoding_as_string, xrange(face.num_charmaps)),
                ))

#####################################################################################################
#
# End
#
#####################################################################################################
