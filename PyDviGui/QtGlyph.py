# -*- coding: utf-8 -*-

####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

__all__= ['QtFtGlyph', 'QtPkGlyph']

####################################################################################################

import logging

import numpy as np

from PyQt4 import QtGui, QtCore

####################################################################################################

from PyDVI.TeXUnit import *

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

class QtFtGlyph(object):

    ##############################################

    def __init__(self, font, glyph_index, magnification):

        # print 'QtFtGlyph', font.name, glyph_index, magnification

        size = magnification * font.tfm.design_font_size # pt
        resolution = 300 # dpi

        glyph = font.get_glyph(glyph_index, size, resolution)

        glyph_bitmap = glyph.glyph_bitmap

        np_bitmap = np.fromstring(glyph_bitmap.bitmap, dtype=np.uint8)
        np_bitmap.shape = glyph_bitmap.rows, glyph_bitmap.width

        glyph_image = gray_array_to_qimage(np_bitmap)
        
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)

        glyph_pixmap.loadFromData(QtCore.QByteArray(glyph_bitmap.bitmap))

        # print 'size:', size
        # print 'resolution:', resolution
        # print 'width:', glyph_bitmap.width
        # print 'height:', glyph_bitmap.rows
        # print 'left:', glyph_bitmap.left
        # print 'top:', glyph_bitmap.top

        self.pixmap = glyph_pixmap

        self.width  = glyph_bitmap.width
        self.height = glyph_bitmap.rows
        self.horizontal_offset = glyph_bitmap.left
        self.vertical_offset = - glyph_bitmap.top

        # Fixme: Compute once?
        self.h_scale = magnification*dpi2mm(resolution)
        self.v_scale = magnification*dpi2mm(resolution)

####################################################################################################

class QtPkGlyph(object):

    ##############################################

    def __init__(self, font, glyph_index, magnification):

        # print 'QtPkGlyph', font.name, glyph_index, magnification

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
        # |    |     |
        # |    |     |
        # +----+-----+---
        # |    |     |
        # |    +-----+
        # |  
        #

        self.width  = glyph.width
        self.height = glyph.height
        self.horizontal_offset = -glyph.horizontal_offset
        self.vertical_offset   = -glyph.vertical_offset

        # Fixme: Compute once?
        self.h_scale = magnification*dpi2mm(glyph.pk_font.horizontal_dpi)
        self.v_scale = magnification*dpi2mm(glyph.pk_font.vertical_dpi)

####################################################################################################
#
# End
#
####################################################################################################
