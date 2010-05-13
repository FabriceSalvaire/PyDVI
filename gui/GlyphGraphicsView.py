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
#  - 23/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

import math

from PyQt4 import QtGui, QtCore

#####################################################################################################

from PyDVI.PkFont import PkFont
from PyDVI.TeXUnit import *
from PyDVI.Type1Font import Type1Font

from QtGlyph import QtPkGlyph, QtFtGlyph

#####################################################################################################

class GlyphGraphicsView(QtGui.QGraphicsView):

    ###############################################

    def __init__(self, parent):

        super(GlyphGraphicsView, self).__init__(parent)

        self.scene = scene = QtGui.QGraphicsScene(self)

        scene.setSceneRect(-1, -1, 1, 1)

        self.setScene(scene)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.setRenderHints(QtGui.QPainter.Antialiasing
                            |QtGui.QPainter.HighQualityAntialiasing
                            |QtGui.QPainter.SmoothPixmapTransform
                            |QtGui.QPainter.TextAntialiasing
                            )

        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

    ###############################################

    def show_glyph(self, font, glyph_index):
   
        self.scene.clear()

        if isinstance(font, Type1Font):
            self.add_type1_char(font, glyph_index)
        elif isinstance(font, PkFont):
            self.add_pk_char(font, glyph_index)

        self.add_grid()
        self.add_glyph_box()

        self.scene.update()

    ###############################################

    def add_glyph_box(self):

        qt_glyph = self.qt_glyph

        pen = QtGui.QPen(QtCore.Qt.red, .5)

        char_box = QtCore.QRectF(qt_glyph.horizontal_offset, qt_glyph.vertical_offset,
                                 qt_glyph.width, qt_glyph.height)

        char_box_item = self.scene.addRect(char_box, pen)
        char_box_item.scale(qt_glyph.h_scale, qt_glyph.v_scale)

    ###############################################

    def add_grid(self):

        x_min, x_max = -5, 5
        y_min, y_max = -5, 5

        width, height = y_max - y_min, x_max - x_min

        grid_spacing = 1. # mm
        sub_grid_divider = 10
        sub_grid_spacing = grid_spacing / sub_grid_divider

        grid_pen = QtGui.QPen(QtCore.Qt.blue, .01)
        sub_grid_pen = QtGui.QPen(QtCore.Qt.green, .01)

        def grid_iterator(min, max, painter):
            x = min
            while x <= max:
                painter(x, grid_pen)
                xx = x + sub_grid_spacing
                if x < max:
                    for i in xrange(1, sub_grid_divider):
                        painter(xx, sub_grid_pen)
                        xx += sub_grid_spacing
                x += grid_spacing

        paint_hline = lambda x, pen: self.scene.addRect(QtCore.QRectF(x, y_min, 0, height), pen)
        paint_vline = lambda y, pen: self.scene.addRect(QtCore.QRectF(x_min, y, width, 0), pen)

        grid_iterator(x_min, x_max, paint_hline)
        grid_iterator(y_min, y_max, paint_vline)

    ###############################################

    def add_type1_char(self, font, glyph_index):

        self.qt_glyph = qt_glyph = QtFtGlyph(font, glyph_index, magnification = 1)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)
        char_pixmap_item.scale(qt_glyph.h_scale, qt_glyph.v_scale)

    ###############################################

    def add_pk_char(self, font, glyph_index):

        self.qt_glyph = qt_glyph = QtPkGlyph(font, glyph_index, magnification = 1)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)
        char_pixmap_item.scale(qt_glyph.h_scale, qt_glyph.v_scale)

    ###############################################

    def keyPressEvent(self, event):

        key = event.key()

        dx = 10

        print 'keyPressEvent', key

        if key == QtCore.Qt.Key_Up:
            self.translate(0, -dx)

        elif key == QtCore.Qt.Key_Down:
            self.translate(0, dx)

        elif key == QtCore.Qt.Key_Left:
            self.translate(-dx, 0)

        elif key == QtCore.Qt.Key_Right:
            self.translate(dx, 0)

        elif key == QtCore.Qt.Key_Plus:
            self.scale_view(2)

        elif key == QtCore.Qt.Key_Minus:
            self.scale_view(.5)

        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    ###############################################

    def wheelEvent(self, event):

        delta = event.delta()

        if delta > 0:
            self.scale_view(2)
        else:
            self.scale_view(0.5)

    ###############################################

    def scale_view(self, scale_factor):

        transformation = self.matrix().scale(scale_factor, scale_factor)

        factor = transformation.mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.1 or factor > 1000:
            return

        self.scale(scale_factor, scale_factor)

#####################################################################################################
#
# End
#
#####################################################################################################
