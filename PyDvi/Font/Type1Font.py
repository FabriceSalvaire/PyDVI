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

    def font_size(self, font_size, resolution=600):

        key = "{}@{}".format(font_size, resolution)
        if font_size not in self._font_size:
            self._font_size[key] = FontSize(self, font_size, resolution)
        return self._font_size[key]

    ##############################################

    def get_glyph(self, glyph_index, size, resolution=600):

        self._logger.info("glyph[{}] @size {} @resolution {} dpi".format(glyph_index, size, resolution))

        font_size = self.font_size(size, resolution)

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

    def __init__(self, font, font_size, resolution=600):

        self._font = font
        self._size = font_size
        self._resolution = resolution

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

    @property
    def resolution(self):
        return self._resolution

    ##############################################

    def __getitem__(self, charcode): #!# in fact glyph_index

        if charcode not in self._glyphs:
            # Converts the integer to the corresponding unicode character before printing.
            #!# self.load_glyph(u'%c' % charcode) # Fixme: %c ?
            self.load_glyph(charcode)
        return self._glyphs[charcode]

    ##############################################

    def load_all_glyphs(self):

        face = self._font._face
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            self.load_glyph(unichr(charcode))
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

    ##############################################
 
    def _set_face_transfrom(self):

        face = self._font._face
        horizontal_scale = 100
        resolution = self._resolution # dpi
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

        flags = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT
        # flags |= freetype.FT_LOAD_TARGET_LCD

        #!# face.load_char(charcode, flags)
        glyph_index = charcode
        face.load_glyph(glyph_index, flags) # Fixme: index using charcode

        bitmap = face.glyph.bitmap # a list
        left = face.glyph.bitmap_left
        top = face.glyph.bitmap_top
        width = face.glyph.bitmap.width
        rows = face.glyph.bitmap.rows
        pitch = face.glyph.bitmap.pitch # stride / number of bytes taken by one bitmap row

        # Remove padding
        data = np.array(bitmap.buffer).reshape(rows, pitch)
        data = data[:,:width].astype(np.ubyte)
        
        # Gamma correction
        # gamma = 1.5
        # Z = (data/255.0)**gamma
        # data = Z*255

        # Build glyph
        size = data.shape[1], data.shape[0]
        offset = left, top
        advance = face.glyph.advance.x, face.glyph.advance.y
        glyph = Glyph(self, charcode, size, offset, advance)
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

    def __init__(self, font_size, charcode, size, offset, advance):

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
        """

        self.font_size = font_size
        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance

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
