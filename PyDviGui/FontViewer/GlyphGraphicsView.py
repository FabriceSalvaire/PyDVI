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

import logging

from PyQt4 import QtGui, QtCore

####################################################################################################

from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.Type1Font import Type1Font
from PyDvi.TeXUnit import *

from .Glyph import PkGlyph, FtGlyph

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlyphGraphicsView(QtGui.QGraphicsView):

    _logger = _module_logger.getChild('GlyphGraphicsView')

    ##############################################

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

    ##############################################

    def fit_view(self):

        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    ##############################################

    def show_glyph(self, font, glyph_index):
   
        self.scene.clear()

        if isinstance(font, Type1Font):
            self.add_type1_char(font, glyph_index)
        elif isinstance(font, PkFont):
            self.add_pk_char(font, glyph_index)

        self.add_grid()
        self.add_glyph_box()

        self.scene.update()

        return self._glyph.glyph # Fixme: naming ...

    ##############################################

    def add_glyph_box(self):

        glyph = self._glyph

        pen = QtGui.QPen(QtCore.Qt.red, .5)

        char_box = QtCore.QRectF(glyph.horizontal_offset, glyph.vertical_offset,
                                 glyph.width, glyph.height)

        char_box_item = self.scene.addRect(char_box, pen)
        char_box_item.scale(glyph.h_scale, glyph.v_scale)

    ##############################################

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

    ##############################################

    def _add_glyph(self, glyph):

        self._glyph = glyph
        char_pixmap_item = self.scene.addPixmap(glyph.pixmap)
        char_pixmap_item.setOffset(glyph.horizontal_offset, glyph.vertical_offset)
        char_pixmap_item.scale(glyph.h_scale, glyph.v_scale)

    ##############################################

    def add_type1_char(self, font, glyph_index):

        self._add_glyph(FtGlyph(font, glyph_index, magnification=1))

    ##############################################

    def add_pk_char(self, font, glyph_index):

        self._add_glyph(PkGlyph(font, glyph_index, magnification=1))

    ##############################################

    def keyPressEvent(self, event):

        dx = 10

        key = event.key()
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

    ##############################################

    def wheelEvent(self, event):

        delta = event.delta()
        if delta > 0:
            self.scale_view(2)
        else:
            self.scale_view(0.5)

    ##############################################

    def scale_view(self, scale_factor):

        transformation = self.matrix().scale(scale_factor, scale_factor)
        factor = transformation.mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.1 or factor > 1000:
            return
        self.scale(scale_factor, scale_factor)

####################################################################################################
#
# End
#
####################################################################################################
