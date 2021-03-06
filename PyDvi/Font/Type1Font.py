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

__all__ = ['Type1Font']

####################################################################################################

import logging
import unicodedata

import numpy as np

import freetype

####################################################################################################

from ..Kpathsea import kpsewhich
from .Font import Font, font_types, FontMetricNotFound

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

    font_type = font_types.Type1
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
        
        if self.tfm is None:
            self._find_afm()

        encodings = [charmap.encoding for charmap in self._face.charmaps]
        if freetype.FT_ENCODING_ADOBE_CUSTOM in encodings:
            encoding = freetype.FT_ENCODING_ADOBE_CUSTOM
        elif freetype.FT_ENCODING_ADOBE_STANDARD in encodings:
            encoding = freetype.FT_ENCODING_ADOBE_STANDARD
        else:
            # encoding = freetype.FT_ENCODING_UNICODE
            raise NameError("Font %s doesn't have an Adobe encoding" % (self.name))
        self._face.select_charmap(encoding)

        self._init_index()

        # self._log_face_information()
        # self._log_glyph_table()

        self._font_size = {}

    ##############################################

    def _find_afm(self):

        # try:
        #     super(Type1Font, self)._find_tfm()
        # except FontMetricNotFound:

        afm_file = kpsewhich(self.name, file_format='afm')
        print afm_file
        if afm_file is None:
            raise NameError("AFM file was not found for font {}".format(self.name))
        else:
            self._logger.info("Attach AFM {}".format(afm_file))
            self._face.attach_file(afm_file)

    ##############################################

    def _init_index(self):

        self._index_to_charcode = {}
        self._charcode_to_index = {}

        face = self._face

        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            unicode_character = unichr(charcode)
            try:
                name = unicodedata.name(unicode_character)
            except ValueError:
                name = '<unknown character>'
            self._index_to_charcode[glyph_index] = (charcode, name)
            self._charcode_to_index[charcode] = (glyph_index, name)
            # face.get_glyph_name(glyph_index) # is not available
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

    ##############################################

    def __len__(self):

        return self._face.num_glyphs

    ##############################################

    def font_size(self, font_size, resolution):

        key = "{}@{}".format(font_size, resolution)
        if font_size not in self._font_size:
            self._font_size[key] = FontSize(self, font_size, resolution)
        return self._font_size[key]

    ##############################################

    def get_glyph(self, tex_glyph_index, size, resolution=600):

        # self._logger.info("glyph[{}] @size {} @resolution {} dpi".format(tex_glyph_index, size, resolution))

        font_size = self.font_size(size, resolution)

        glyph_index, name = self._charcode_to_index[tex_glyph_index]
        # self._logger.info("retrieve glyph {} {}".format(glyph_index, name))
        glyph = font_size[glyph_index]

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
            message += u"  [{}] TeX[{} {}] {} {}\n".format(glyph_index,
                                                           charcode,
                                                           hex(charcode), # 0x%04lx
                                                           unicode_character,
                                                           name)
            # face.get_glyph_name(glyph_index) # is not available
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

        self._logger.info(message)

####################################################################################################

class FontSize(object):

    ##############################################

    def __init__(self, font, font_size, resolution):

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

    def __getitem__(self, glyph_index):

        if glyph_index not in self._glyphs:
            self.load_glyph(glyph_index)
        return self._glyphs[glyph_index]

    ##############################################

    def load_all_glyphs(self):

        face = self._font._face
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            self.load_glyph(glyph_index)
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
 
    def load_glyph(self, glyph_index, lcd=False):

        # Fixme: lcd steering

        if glyph_index in self._glyphs:
            return

        self._set_face_transfrom()

        self.dirty = True

        face = self._font._face

        flags = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT
        if lcd:
            flags |= freetype.FT_LOAD_TARGET_LCD

        face.load_glyph(glyph_index, flags)
        slot = face.glyph

        bitmap = slot.bitmap # a list
        width = slot.bitmap.width
        rows = slot.bitmap.rows
        pitch = slot.bitmap.pitch # stride / number of bytes taken by one bitmap row
        # left: The left-side bearing, i.e., the horizontal distance from the current pen position
        #   to the left border of the glyph bitmap.
        # top: The top-side bearing, i.e., the vertical distance from the current pen position to
        #   the top border of the glyph bitmap. This distance is positive for upwards y!
        left = slot.bitmap_left
        top = slot.bitmap_top

        # Remove padding
        data = np.array(bitmap.buffer).reshape(rows, pitch)
        data = data[:,:width].astype(np.ubyte)
        if lcd:
            # RBG data else grayscale
            glyph_bitmap = data.reshape(rows, width/3, 3)
        else:
            glyph_bitmap = np.zeros((rows, width, 3), dtype=np.ubyte)
            for i in xrange(3):
                glyph_bitmap[:,:,i] = data
        
        # Build glyph
        size = glyph_bitmap.shape[1], glyph_bitmap.shape[0]
        offset = left, top
        advance = slot.advance.x, slot.advance.y

        metrics = slot.metrics
        metrics_px = [from_64th_point(x) for x in (metrics.width,
                                                   metrics.height,
                                                   metrics.horiBearingX,
                                                   metrics.horiBearingY,
                                                   metrics.horiAdvance)]

        glyph = Glyph(self, glyph_index, size, offset, advance, metrics_px)
        glyph.glyph_bitmap = glyph_bitmap # Fixme:
        self._glyphs[glyph_index] = glyph

####################################################################################################

class FontMetrics(object):

    """Font Metrics

    * Ascent
        The distance from the baseline to the highest or upper grid coordinate used to place an
        outline point. It is a positive value, due to the grid's orientation with the Y axis
        upwards.
    * Descent
        The distance from the baseline to the lowest grid coordinate used to place an outline
        point. In FreeType, this is a negative value, due to the grid's orientation. Note that in
        some font formats this is a positive value.
    * Linegap
        The distance that must be placed between two lines of text. The baseline-to-baseline
        distance should be computed as

            linespace = ascent - descent + linegap
        if you use the typographic values.

    """

    ##############################################

    def __init__(self, font_size):

        face = font_size._font._face
        # Fixme: TeX point = 72.27 but FreeType 72 ???
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

    def __init__(self, font_size, glyph_index, size, offset, advance, metrics):

        """

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance
        """

        self.font_size = font_size
        self.glyph_index = glyph_index
        self.size = size
        self.offset = offset
        self.advance = advance

        (self.width_px,
         self.height_px,
         self.horizontal_bearing_x_px,
         self.horizontal_bearing_y_px,
         self.horizontal_advance_px) = metrics

    ##############################################

    def px_to_mm(self, x):
        return 25.4/self.font_size.resolution * x

####################################################################################################
#
# End
#
####################################################################################################
