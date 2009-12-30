# -*- coding: utf-8 -*-

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

__ALL__= ['QtFtGlyph', 'QtPkGlyph']

#####################################################################################################

from PyQt4 import QtGui, QtCore

import numpy as np

#####################################################################################################

from TeXUnit import *

#####################################################################################################

class QtFtGlyph(object):

    ###############################################

    def __init__(self, font, glyph_index, magnification):

        print 'QtFtGlyph', font.name, glyph_index, magnification

        glyph = font.get_glyph(glyph_index, size = 10, resolution = 100)

        glyph_bitmap = glyph.glyph_bitmap

        np_bitmap = np.fromstring(glyph_bitmap.bitmap, dtype=np.uint8)
        np_bitmap.shape = glyph_bitmap.rows, glyph_bitmap.width

        glyph_image = QtGui.QImage(glyph_bitmap.width, glyph_bitmap.rows, QtGui.QImage.Format_ARGB32)
        
        for y in xrange(glyph_bitmap.rows):
            for x in xrange(glyph_bitmap.width):
                gray_level = np_bitmap[y,x]
                if gray_level == 0:
                    argb = (gray_level << 16) + (gray_level << 8) + gray_level # 0 << 24 + 
                    # argb = 0x00FFFFFF
                else:
                    argb = 0xFF000000
                    # print x, y, gray_level, hex(argb)
                glyph_image.setPixel(x, y, int(argb))
        
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)

        glyph_pixmap.loadFromData(QtCore.QByteArray(glyph_bitmap.bitmap))

        print 'Left:', glyph_bitmap.left
        print 'Top:', glyph_bitmap.top

        self.pixmap = glyph_pixmap

        self.horizontal_offset = glyph_bitmap.left
        self.vertical_offset = - glyph_bitmap.top

#####################################################################################################

class QtPkGlyph(object):

    ###############################################

    def __init__(self, font, glyph_index, magnification):

        print 'QtPkGlyph', font.name, glyph_index, magnification

        glyph = font[glyph_index]

        glyph_bitmap = glyph.get_glyph_bitmap()
        
        glyph_image = QtGui.QImage(glyph.width, glyph.height, QtGui.QImage.Format_ARGB32) # Format_Mono
        
        for y in xrange(glyph.height):
            for x in xrange(glyph.width):
                if glyph_bitmap[y, x] == 1:
                    glyph_image.setPixel(x, y, 0xFF000000)
                else:
                    glyph_image.setPixel(x, y, 0x00FFFFFF)
        
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)

        self.pixmap = glyph_pixmap

        self.width = glyph.width
        self.height = glyph.height
        self.horizontal_offset = -glyph.horizontal_offset
        self.vertical_offset   = -glyph.vertical_offset

        self.h_scale = dpi2mm(glyph.pk_font.horizontal_dpi/magnification)
        self.v_scale = dpi2mm(glyph.pk_font.vertical_dpi/magnification)

        print 'Magnification', float(magnification), self.h_scale, self.v_scale

#####################################################################################################
#
# End
#
#####################################################################################################
