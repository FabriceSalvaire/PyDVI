####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
# - 18/12/2011 fabrice
#    char code 0 -> 127 + 1 = 128
#
####################################################################################################

####################################################################################################

__all__ = ['Type1Font']

####################################################################################################

import freetype

####################################################################################################

from PyDVI.Font import Font, font_types
from PyDVI.Tools.Logging import print_card

####################################################################################################

def test_bit(flags, mask):
    return flags & mask == 1

# 1/64th of pixels

def convert_26_6(x):
    return float(x)/2**6

# 1/65536th of pixels

def convert_16_16(x):
    return float(x)/2**16

####################################################################################################

class FtGlyph(object):

    ##############################################

    def __init__(self, font, glyph_index, size, resolution):

        self.font = font
        self.glyph_index = glyph_index
        self.size = size
        self.resolution = resolution

        face = self.font.face

        # The character widths and heights are specified in 1/64th of points. A point is a physical
        # distance, equaling 1/72th of an inch.

        size *= 64
        # Fixme ....
        f.set_char_size(self, width=0, height=0, hres=72, vres=72)
        face.set_char_size()

        self.glyph = face.load_glyph(glyph_index, flags=4)

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

####################################################################################################

class Type1Font(Font):

    font_type = font_types.Pk
    font_type_string = 'PostScript Type1 Font'
    extension = 'pfb'

    ##############################################

    def __init__(self, font_manager, font_id, name):

        super(Type1Font, self).__init__(font_manager, font_id, name)

        self.glyphs = {}

        try:
            self.face = freetype.Face(self.filename)
        except:
            raise NameError("Freetype can't open file %s" % (self.filename))

        try:
            self.face.select_charmap(freetype.FT_ENCODING_UNICODE)
        except:
            raise NameError("Font %s doesn't have an Unicode char map" % (self.name))

    ##############################################

    def __len__(self):

        return self.face.num_glyphs

    ##############################################

    def get_char_index(self, char_code):

        '''
        Return the glyph index of a given character code. This function uses a charmap object to do
        the mapping.
        '''

        return self.face.get_char_index[char_code]

    ##############################################

    def get_glyph_index(self, glyph_name):

        '''
        Return the glyph index of a given glyph name. This function uses driver specific objects to
        do the translation.
        '''

        return self.face.get_name_index(glyph_name)

    ##############################################

    @staticmethod
    def hash_glyph(glyph_index, size, resolution):

        return hex(glyph_index)[2:] + hex(int(640*size))[1:] + hex(resolution)[1:]

    ##############################################

    def get_glyph(self, glyph_index, size, resolution):

        glyph_hash_key = self.hash_glyph(glyph_index, size, resolution)

        if self.glyphs.has_key(glyph_hash_key):
            glyph = self.glyphs[glyph_hash_key]
        else:
            glyph = self.glyphs[glyph_hash_key] = FtGlyph(self, glyph_index, size, resolution)

        return glyph

    ##############################################

    def print_summary(self):

        face = self.face

        string_template = '''
postscript name:     %s
family name:         %s
style name:          %s
number of faces:     %u
number of glyphs:    %u
available sizes:     %s
char maps:           %s
units per em:        %s
flags:               %s
bold:                %s
italic:              %s
scalable:            %s
ascender:            %u
descender:           %u
height:              %u
max advance width:   %u
max advance height:  %u
underline position:  %u
underline thickness: %u
has horizontal:      %s
has vertical:        %s
has kerning:         %s
is fixed width:      %s
is scalable:         %s
'''

        text = string_template % (
            face.postscript_name,
            face.family_name,
            face.style_name,
            face.num_faces,
            len(self),
            str(face.available_sizes),
            str([charmap.encoding_name for charmap in face.charmaps]),
            hex(face.style_flags),
            face.units_per_EM,
            test_bit(face.style_flags, freetype.FT_STYLE_FLAG_BOLD),
            test_bit(face.style_flags, freetype.FT_STYLE_FLAG_ITALIC),
            test_bit(face.style_flags, freetype.FT_FACE_FLAG_SCALABLE),
            face.ascender,
            face.descender,
            face.height,
            face.max_advance_width,
            face.max_advance_height,
            face.underline_position,
            face.underline_thickness,
            face.has_horizontal,
            face.has_vertical,
            face.has_kerning,
            face.is_fixed_width,
            face.is_scalable,
            )

        print_card(self.print_header() + text)

    ##############################################

    def print_glyph_table(self):

        message = 'Glyph Table\n'

        for glyph_index in xrange(1, len(self)):
            message += '\n%6u %s -> %s' % (
                glyph_index,
                self.get_glyph_name(glyph_index),
                self.glyph_index_to_unicodes[glyph_index],
                )

        print_card(message)

####################################################################################################
#
# End
#
####################################################################################################
