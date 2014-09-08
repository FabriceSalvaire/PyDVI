# -*- coding: utf-8 -*-

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

__all__= ['FtGlyph', 'PkGlyph']

####################################################################################################

import logging

import numpy as np

from PyQt4 import QtGui, QtCore

####################################################################################################

from PyDvi.TeXUnit import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def array_to_qimage(np_array):

    # Fixme: some glyphs are painted correctly but most show a dephasing between rows ?
        
    if len(np_array.shape) != 2:
        raise ValueError("array_to_qimage can only convert 2D arrays")
    height, width = np_array.shape
    _np_array = np.require(np_array, np.uint8, 'C')
    image = QtGui.QImage(_np_array.data, width, height, QtGui.QImage.Format_Indexed8)
    
    return image

####################################################################################################

def create_indexed_qimage(height, width):

    return QtGui.QImage(width, height, QtGui.QImage.Format_Indexed8)

####################################################################################################

def init_bitmap_index(image):

    for i in xrange(256):
        image.setColor(i, QtGui.QColor(255, 255, 255).rgb())
    image.setColor(1, QtGui.QColor(0, 0, 0).rgb())

####################################################################################################

def init_gray_index(image):

    for i in xrange(256):
        j = 255 -i
        image.setColor(i, QtGui.QColor(j, j, j).rgb())

####################################################################################################

def init_pixels(np_array, image):

    height, width = np_array.shape
    for y in xrange(height):
        for x in xrange(width):
            image.setPixel(x, y, int(np_array[y, x]))

####################################################################################################

def bitmap_array_to_qimage(np_array):

    """Convert the 2D numpy array `np_array` into a 8-bit QImage with a bitmap colormap.  The first
    dimension represents the vertical image axis."""

    # image = array_to_qimage(np_array)
    image = create_indexed_qimage(* np_array.shape)
    init_bitmap_index(image)
    init_pixels(np_array, image)
    
    return image

####################################################################################################

def gray_array_to_qimage(np_array):

    """Convert the 2D numpy array `np_array` into a 8-bit QImage with a gray colormap.  The first
    dimension represents the vertical image axis."""
    
    # image = array_to_qimage(np_array)

    image = create_indexed_qimage(* np_array.shape)
    init_gray_index(image)
    init_pixels(np_array, image)
    
    return image

####################################################################################################

class FtGlyph(object):

    _logger = _module_logger.getChild('FtGlyph')

    ##############################################

    def __init__(self, font, glyph_index, magnification):

        self._logger.info("font {} glyph[{}] @mag {}".format(font.name, glyph_index, magnification))

        # size: 47 57  offset: -2 -56 scale: 0.042 0.042
        # versus Pk
        # size: 45 57  offset: 3 -56 scale: 0.042 0.042
        #  25.4 mm / 600 dpi * 50 px = 2.12 mm versus 2.11 mm 
        size = magnification * font.tfm.design_font_size # pt

        glyph = font.get_glyph(glyph_index, size)
        glyph_bitmap = glyph.glyph_bitmap
        glyph_bitmap = 255 - glyph_bitmap

        # glyph_image = gray_array_to_qimage(glyph_bitmap)
        glyph_image = QtGui.QImage(glyph_bitmap.tostring(),
                                   glyph_bitmap.shape[1], glyph_bitmap.shape[0],
                                   glyph_bitmap.shape[1]*3,
                                   QtGui.QImage.Format_RGB888)
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)
        self.pixmap = glyph_pixmap

        self.width = glyph_bitmap.shape[1]
        self.height = glyph_bitmap.shape[0]
        self.horizontal_offset = -glyph.offset[0]
        self.vertical_offset = -glyph.offset[1]

        # Fixme: Compute once?
        resolution = glyph.font_size.resolution
        self.h_scale = magnification*dpi2mm(resolution)
        self.v_scale = magnification*dpi2mm(resolution)

        template = "size: {} {}  offset: {} {} scale: {:4.3f} {:4.3f}"
        self._logger.info(template.format(self.width, self.height,
                                          self.horizontal_offset, self.vertical_offset, 
                                          self.h_scale, self.v_scale))

####################################################################################################

class PkGlyph(object):

    _logger = _module_logger.getChild('PkGlyph')

    ##############################################

    def __init__(self, font, glyph_index, magnification):

        self._logger.info("font {} glyph[{}] @mag {}".format(font.name, glyph_index, magnification))

        glyph = font[glyph_index]
        glyph_bitmap = glyph.get_glyph_bitmap()

        glyph_image = bitmap_array_to_qimage(glyph_bitmap)
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)
        self.pixmap = glyph_pixmap

        #
        # Pk convention
        #
        # | (-h,v)
        # |    +-----+
        # |    |     |
        # +----+-----+---
        # |    |     |
        # |    +-----+
        # |  
        #

        self.width = glyph.width
        self.height = glyph.height
        self.horizontal_offset = -glyph.horizontal_offset
        self.vertical_offset = -glyph.vertical_offset

        # Fixme: Compute once?
        self.h_scale = magnification*dpi2mm(glyph.pk_font.horizontal_dpi)
        self.v_scale = magnification*dpi2mm(glyph.pk_font.vertical_dpi)

        # font cmr10 glyph[0] @mag 1
        # size: 45 57  offset: 3 -56 scale: 0.042 0.042
        #  25.4 mm / 600 dpi * 50 px = 2.12 mm versus 2.11 mm 
        template = "size: {} {}  offset: {} {} scale: {:4.3f} {:4.3f}"
        self._logger.info(template.format(self.width, self.height,
                                          self.horizontal_offset, self.vertical_offset, 
                                          self.h_scale, self.v_scale))

####################################################################################################
#
# End
#
####################################################################################################
