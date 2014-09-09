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

import logging

####################################################################################################

from PyOpenGLng.HighLevelApi.TextureAtlas import TextureAtlas

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class TextureFont(object):

    _logger = _module_logger.getChild('TextureFont')

    ##############################################

    def __init__(self, font):

        self._logger.info('')

        self._font = font

        # Fixme: an atlas could be shared by several fonts and sizes
        atlas_size = 1024
        self._atlas = TextureAtlas(atlas_size, atlas_size, depth=3) # Fixme: using lcd rendering
        self._dirty = False

        self._glyphs = {}

    ##############################################

    @property
    def name(self):
        return self._font.name

    @property
    def atlas(self):
        return self._atlas

    ##############################################
 
    def _load_glyph(self, glyph_index, magnification):

        self._logger.info("load glyph[{}]*{}".format(glyph_index, magnification))

        atlas = self._atlas

        size = magnification * self._font.tfm.design_font_size # pt

        glyph = self._font.get_glyph(glyph_index, size)
        glyph_bitmap = glyph.glyph_bitmap
        rows, width = glyph_bitmap.shape[:2] # depth

        # Glyphes are separated by a margin
        # margin = 1 # px
        # dimension are given in pixel thus we correct the bitmap width
        x, y, w, h = atlas.get_region(width +2, rows +2)
        if x == -1:
            raise NameError("Cannot allocate glyph in atlas")
        x, y = x+1, y+1
        w, h = w-2, h-2 # = width/depth, rows
        atlas.set_region((x, y, w, h), glyph_bitmap)

        # Compute texture coordinates
        u0 = x / float(atlas.width)
        v0 = y / float(atlas.height)
        u1 = (x + w) / float(atlas.width)
        v1 = (y + h) / float(atlas.height)

        # Fixme: better idea?
        glyph.texture_coordinates = (u0, v0, u1, v1)

        return glyph

    ##############################################
 
    def glyph(self, glyph_index, magnification):

        key = "{}-{}".format(glyph_index, magnification)
        if key not in self._glyphs:
            self._glyphs[key] = self._load_glyph(glyph_index, magnification)
        return self._glyphs[key]

####################################################################################################
# 
# End
# 
####################################################################################################
