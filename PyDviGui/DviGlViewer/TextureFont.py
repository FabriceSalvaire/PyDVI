####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
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
        self._atlas = TextureAtlas(atlas_size, atlas_size, depth=1) # Fixme: 3
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
        x, y, w, h = atlas.get_region(width/atlas.depth +2, rows +2)
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
        texture_coordinate = (u0, v0, u1, v1)

        # Fixme: store glyph or texture_coordinate ?

        return texture_coordinate

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
