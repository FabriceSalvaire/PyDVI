####################################################################################################
# 
# PyDvi - A Python Library to Process DVI Stream
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

import logging
import unicodedata

import numpy as np

import freetype

####################################################################################################

from .Font import Font, font_types

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def from_64th_point(x):
    return x/64.

def to_64th_point(x):
    return x*64

####################################################################################################

def test_bit(flags, mask):
    return flags & mask == 1

####################################################################################################

# # 1/64th of pixels

# def convert_26_6(x):
#     return float(x)/2**6

# # 1/65536th of pixels

# def convert_16_16(x):
#     return float(x)/2**16

####################################################################################################

# class FtGlyph(object):

#     ##############################################

#     def __init__(self, font, glyph_index, size, resolution):

#         self.font = font
#         self.glyph_index = glyph_index
#         self.size = size
#         self.resolution = resolution

#         face = self.font._face

#         # The character widths and heights are specified in 1/64th of points. A point is a physical
#         # distance, equaling 1/72th of an inch.

#         size *= 64
#         # Fixme ....
#         f.set_char_size(self, width=0, height=0, hres=72, vres=72)
#         face.set_char_size()

#         self.glyph = face.load_glyph(glyph_index, flags=4)

#         # print 'Char Box:', map(convert_26_6, self.glyph.getCBox(ft2.ft_glyph_bbox_subpixels))
#         # print 'Advance:', map(convert_16_16, self.glyph.advance)

#         posx, posy = 0, 0
#         self.glyph_bitmap = ft2.Bitmap(self.glyph, ft2.FT_RENDER_MODE_NORMAL, posx, posy)

#         # bitmap = np.fromstring(glyph_bitmap.bitmap, dtype=np.uint8)
#         # bitmap.shape = glyph_bitmap.rows, glyph_bitmap.width
#         # print 'Bitmap shape:', bitmap.shape

#         # print 'Left:', self.glyph_bitmap.left
#         # print 'Top:', self.glyph_bitmap.top
#         # print 'Number of grays:', self.glyph_bitmap.num_grays
#         # print 'Pixel Mode:', self.glyph_bitmap.pixel_mode
#         # print 'Palette Mode:', self.glyph_bitmap.palette_mode

####################################################################################################

class Type1Font(Font):

    _logger = _module_logger.getChild('Type1Font')

    font_type = font_types.Pk
    font_type_string = 'PostScript Type1 Font'
    extension = 'pfb'

    ##############################################

    def __init__(self, font_manager, font_id, name):

        super(Type1Font, self).__init__(font_manager, font_id, name)

        # self._glyphs = {}

        try:
            self._face = freetype.Face(self.filename)
        except:
            raise NameError("Freetype can't open file %s" % (self.filename))

        try:
            self._face.select_charmap(freetype.FT_ENCODING_UNICODE)
        except:
            raise NameError("Font %s doesn't have an Unicode char map" % (self.name))

        self._init_index()

        self._log_face_information()
        self._log_glyph_table()

        self._font_size = {}

    ##############################################

    def _init_index(self):

        self._index_to_charcode = {}

        face = self._face

        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            unicode_character = unichr(charcode)
            try:
                name = unicodedata.name(unicode_character)
            except ValueError:
                name = '<unknown character>'
            self._index_to_charcode[glyph_index] = (charcode, name)
            # face.get_glyph_name(glyph_index) # is not available
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

    ##############################################

    def __len__(self):

        return self._face.num_glyphs

    ##############################################

    def font_size(self, font_size):

        if font_size not in self._font_size:
            self._font_size[font_size] = FontSize(self, font_size)
        return self._font_size[font_size]

    # ##############################################

    # def get_char_index(self, char_code):

    #     '''
    #     Return the glyph index of a given character code. This function uses a charmap object to do
    #     the mapping.
    #     '''

    #     return self._face.get_char_index[char_code]

    # ##############################################

    # def get_glyph_index(self, glyph_name):

    #     '''
    #     Return the glyph index of a given glyph name. This function uses driver specific objects to
    #     do the translation.
    #     '''

    #     return self._face.get_name_index(glyph_name)

    # ##############################################

    # @staticmethod
    # def hash_glyph(glyph_index, size, resolution):

    #     return hex(glyph_index)[2:] + hex(int(640*size))[1:] + hex(resolution)[1:]

    ##############################################

    def get_glyph(self, glyph_index, size, resolution):

        self._logger.info("glyph[{}] @size {} @resolution {} dpi".format(glyph_index, size, resolution))

        font_size = self.font_size(size)

        # glyph_hash_key = self.hash_glyph(glyph_index, size, resolution)

        # if glyph_hash_key in self._glyphs:
        #     glyph = self._glyphs[glyph_hash_key]
        # else:
        #     glyph = self._glyphs[glyph_hash_key] = FtGlyph(self, glyph_index, size, resolution)

        glyph_index += 1 # Fixme: ???
        charcode, name = self._index_to_charcode[glyph_index]
        self._logger.info("retrieve glyph {} {}".format(charcode, name))
        glyph = font_size[glyph_index] #!# charcode

        return glyph

    ##############################################

    def _log_face_information(self):

        face = self._face

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

        self._logger.info(text)

    ##############################################

    def _log_glyph_table(self):

        face = self._face

        message = 'Glyph Table\n'
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            unicode_character = unichr(charcode)
            try:
                name = unicodedata.name(unicode_character)
            except ValueError:
                name = '<unknown character>'
            message += "  [%d] 0x%04lx %s %s\n" % (glyph_index,
                                                 charcode,
                                                 unicode_character,
                                                 name)
            # face.get_glyph_name(glyph_index) # is not available
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

        self._logger.info(message)

####################################################################################################

class FontSize(object):

    ##############################################

    def __init__(self, font, font_size):

        self._font = font
        self._size = font_size

        self._metrics = FontMetrics(self)
        self._glyphs = {}

    ##############################################

    @property
    def font(self):
        return self._font

    @property
    def size(self):
        return self._size

    @property
    def metrics(self):
        return self._metrics

    ##############################################

    def __getitem__(self, charcode): #!# in fact glyph_index

        if charcode not in self._glyphs:
            # Converts the integer to the corresponding unicode character before printing.
            #!# self.load_glyph(u'%c' % charcode) # Fixme: %c ?
            self.load_glyph(charcode)
        return self._glyphs[charcode]

    ##############################################

    def load_all_glyphs(self):

        # self.load_from_string(string.printable)

        face = self._font._face
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            self.load_glyph(unichr(charcode))
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

    ##############################################
 
    def load_from_string(self, charcodes):

        for charcode in charcodes:
            self.load_glyph(charcode)

    ##############################################
 
    def _set_face_transfrom(self):

        face = self._font._face
        horizontal_scale = 100
        resolution = 72 # dpi
        face.set_char_size(int(to_64th_point(self._size)), 0,
                           horizontal_scale*resolution, resolution)
        # Matrix cooeficients are expressed in 16.16 fixed-point units.
        # 2**16 = 0x10000L = 65536
        matrix = freetype.Matrix(2**16/horizontal_scale, 0,
                                 0, 2**16)
        # The vector coordinates are expressed in 1/64th of a pixel
        # (also known as 26.6 fixed-point numbers).
        delta = freetype.Vector(0, 0)
        face.set_transform(matrix, delta)

        freetype.set_lcd_filter(freetype.FT_LCD_FILTER_LIGHT)

    ##############################################
 
    def load_glyph(self, charcode): #!# in fact glyph_index

        if charcode in self._glyphs:
            return

        self._set_face_transfrom()

        self.dirty = True

        face = self._font._face
        #!# atlas = self._font._atlas

        flags = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT
        #!# if atlas.depth == 3:
        #!# flags |= freetype.FT_LOAD_TARGET_LCD

        #!# face.load_char(charcode, flags)
        glyph_index = charcode
        face.load_glyph(glyph_index, flags) # Fixme: index using charcode

        bitmap = face.glyph.bitmap # a list
        left = face.glyph.bitmap_left
        top = face.glyph.bitmap_top
        width = face.glyph.bitmap.width
        rows = face.glyph.bitmap.rows
        pitch = face.glyph.bitmap.pitch # stride / number of bytes taken by one bitmap row

        # Glyphes are separated by a margin
        # margin = 1 # px
        # dimension are given in pixel thus we correct the bitmap width
        #!# x, y, w, h = atlas.get_region(width/atlas.depth +2, rows +2)
        #!# if x == -1:
        #!#     raise NameError("Cannot allocate glyph in atlas")
        #!# x, y = x+1, y+1
        #!# w, h = w-2, h-2 # = width/depth, rows

        # Remove padding
        data = np.array(bitmap.buffer).reshape(rows, pitch)
        data = data[:,:width].astype(np.ubyte)
        #!# data = data.reshape(rows, width/atlas.depth, atlas.depth)
        
        # Gamma correction
        # gamma = 1.5
        # Z = (data/255.0)**gamma
        # data = Z*255

        #!# atlas.set_region((x, y, w, h), data)

        # Compute texture coordinates
        #!# u0 = x / float(atlas.width)
        #!# v0 = y / float(atlas.height)
        #!# u1 = (x + w) / float(atlas.width)
        #!# v1 = (y + h) / float(atlas.height)
        #!# texture_coordinate = (u0, v0, u1, v1)
        texture_coordinate = (0, 0, 0, 0)

        # Build glyph
        #!# size = w, h
        size = 0, 0
        offset = left, top
        advance = face.glyph.advance.x, face.glyph.advance.y
        glyph = Glyph(charcode, size, offset, advance, texture_coordinate)
        glyph.glyph_bitmap = data # Fixme:
        self._glyphs[charcode] = glyph

        # Generate kerning
        # Fixme: exhaustive?
        for glyph2 in self._glyphs.values():
            self._set_kerning(glyph, glyph2)
            self._set_kerning(glyph2, glyph)

    ##############################################

    def _set_kerning(self, glyph1, glyph2):

        charcode1 = glyph1.charcode
        charcode2 = glyph2.charcode
        face = self._font._face
        kerning = face.get_kerning(charcode2, charcode1, mode=freetype.FT_KERNING_UNFITTED)
        if kerning.x != 0:
            # 64 * 64 because of 26.6 encoding AND the transform matrix
            glyph1._kerning[charcode2] = kerning.x / float(64**2)

####################################################################################################

class FontMetrics(object):

    ##############################################

    def __init__(self, font_size):

        face = font_size._font._face
        face.set_char_size(int(to_64th_point(font_size.size)))
        metrics = face.size

        self.ascender = from_64th_point(metrics.ascender)
        self.descender = from_64th_point(metrics.descender)
        self.height = from_64th_point(metrics.height)
        self.linegap = self.height - self.ascender + self.descender # Fixme: check

####################################################################################################

class Glyph(object):

    """
    A glyph gathers information relative to the size/offset/advance and texture coordinates
    of a single character. It is generally built automatically by a Font.
    """

    def __init__(self, charcode, size, offset, advance, texture_coordinates):

        """
        Build a new glyph

        Parameter:
        ----------

        charcode : char
            Represented character

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance

        texture_coordinates: tuple of 4 floats
            Texture coordinates of bottom-left and top-right corner
        """

        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance
        self.texture_coordinates = texture_coordinates

        self._kerning = {}

    ##############################################

    def get_kerning(self, charcode):

        """ Get kerning information

        Parameters:
        -----------

        charcode: char
            Character preceding this glyph
        """

        return self._kerning.get(charcode, 0)

####################################################################################################
#
# End
#
####################################################################################################
