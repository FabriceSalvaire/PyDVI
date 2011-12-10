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
#    char code 0 -> 127 + 1 = 128
#
#####################################################################################################

#####################################################################################################

__all__ = ['Type1Font']

#####################################################################################################

#!# import ft2

#####################################################################################################

from PyDVI.Font import *
from PyDVI.Tools.Logging import print_card

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

        # The character widths and heights are specified in 1/64th of points. A point is a physical
        # distance, equaling 1/72th of an inch.

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

    def __init__(self, font_manager, font_id, name):

        super(Type1Font, self).__init__(font_manager, font_id, name)

        self.__load_font()
        self.__init_char_map()

        self.glyphs = {}

    ###############################################

    def __len__(self):

        return self.face.num_glyphs

    ###############################################

    def __load_font(self):

        try:
            self.face = ft2.Face(self.font_manager.freetype_library, self.filename, 0) # Fixme: index 0?
        except:
            raise NameError("Freetype can't open file %s" % (self.filename))

    ###############################################

    def __init_char_map(self):

        if not self.set_unicode_char_map():
            raise NameError("Font %s doesn't have an Unicode char map" % (self.name))

        self.glyph_index_to_unicodes = [None]*len(self)

        for unicode_index, glyph_index in self.encoding_vector.iteritems():
            if self.glyph_index_to_unicodes[glyph_index] is None:
                self.glyph_index_to_unicodes[glyph_index] = [unicode_index]
            else:
                self.glyph_index_to_unicodes[glyph_index].append(unicode_index)

            # print '%5u -> %5u %s' % (unicode_index, glyph_index, self.get_glyph_name(glyph_index))
            
    ###############################################

    def get_char_map(self, i):

        return ft2.CharMap(self.face, i)

    ###############################################

    def set_unicode_char_map(self):

        for i in range(self.face.num_charmaps):
            
            charmap = self.get_char_map(i)
            
            if charmap.encoding_as_string == 'unic':
                self.face.setCharMap(charmap)
                self.encoding_vector = self.face.encodingVector()
                return True

        return False

    ###############################################

    def glyph_index_to_unicode(self, glyph_index):

        return self.face.getCharCode[glyph_index]

    ###############################################

    def get_char_index(self, char_code):

        '''
        Return the glyph index of a given character code. This function uses a charmap object to do
        the mapping.
        '''

        return self.face.getCharIndex[char_code]

    ###############################################

    def get_glyph_name(self, glyph_index):

        '''
        Retrieve the ASCII name of a given glyph in a face.
        '''

        return self.face.getGlyphName(glyph_index)

    ###############################################

    def get_glyph_index(self, glyph_name):

        '''
        Return the glyph index of a given glyph name. This function uses driver specific objects to
        do the translation.
        '''

        return self.face.getNameIndex(glyph_name)

    ###############################################

    @staticmethod
    def hash_glyph(glyph_index, size, resolution):

        return hex(glyph_index)[2:] + hex(int(640*size))[1:] + hex(resolution)[1:]

    ###############################################

    def get_glyph(self, glyph_index, size, resolution):

        glyph_hash_key = self.hash_glyph(glyph_index, size, resolution)

        if self.glyphs.has_key(glyph_hash_key):
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
                len(self),
                hex(face.style_flags),
                face.units_per_EM,
                test_bit(face.style_flags, ft2.FT_STYLE_FLAG_BOLD),
                test_bit(face.style_flags, ft2.FT_STYLE_FLAG_ITALIC),
                test_bit(face.style_flags, ft2.FT_FACE_FLAG_SCALABLE),
                [self.get_char_map(i).encoding_as_string for i in xrange(face.num_charmaps)],
                ))

    ###############################################

    def print_glyph_table(self):

        message = 'Glyph Table\n'

        for glyph_index in xrange(1, len(self)):
            message += '\n%6u %s -> %s' % (
                glyph_index,
                self.get_glyph_name(glyph_index),
                self.glyph_index_to_unicodes[glyph_index],
                )

        print_card(message)

#####################################################################################################
#
# End
#
#####################################################################################################
