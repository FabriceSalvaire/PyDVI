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

from PyDvi.Dvi.DviMachine import DviMachine
from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.Type1Font import Type1Font
from PyDvi.TeXUnit import *

####################################################################################################

from .TextureFont import TextureFont

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlDviMachine(DviMachine):

    _logger = _module_logger.getChild('GlDviMachine')
    
    ##############################################

    def __init__(self, font_manager):

        super(GlDviMachine, self).__init__(font_manager)

        self._texture_fonts = {}
        self._glyphs = {} # index by font name

    ##############################################

    def paint_rule(self, x, y, w, h):

        self._logger.info("\nrule ({}, {}) +({}, {})".format(x, y, w, h))

        x_mm, y_mm, w_mm, h_mm = map(sp2mm, (x, y, w, h))
        # print 'paint_rule', x_mm, y_mm, w_mm, h_mm
        # rule_rect = QtCore.QRectF(x_mm, y_mm - h_mm, w_mm, h_mm)
        # pen = QtGui.QPen(QtCore.Qt.black)
        # brush = QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern)
        # rule_item = self.scene.addRect(rule_rect, pen, brush)

    ##############################################

    def paint_char_box(self, char_bounding_box):

        x, y = char_bounding_box.x.inf, char_bounding_box.y.inf
        x_mm, y_mm = map(sp2mm, (x, y))
        box_width  = sp2mm(char_bounding_box.x.length())
        box_height = sp2mm(char_bounding_box.y.length())
        # red_pen = QtGui.QPen(QtCore.Qt.red)
        # char_box_rect = QtCore.QRectF(x_mm, y_mm, box_width, box_height)
        # char_box_item = self.scene.addRect(char_box_rect, red_pen)

    ##############################################

    def paint_char(self, xg, yg, char_bounding_box, font, glyph_index, magnification):

        self._logger.info("\nchar ({}, {}) {} {}[{}]@{}".format(xg, yg, char_bounding_box,
                                                                font.name, glyph_index, magnification))

        # self.paint_char_box(char_bounding_box)

        xg_mm, yg_mm = map(sp2mm, (xg, yg))
        yg_mm = 297 - yg_mm # Fixme: opengl frame

        if font.name not in self._texture_fonts:
            textures_font = TextureFont(font)
            self._texture_fonts[font.name] = textures_font
            self._glyphs[font.name] = []
        else:
            textures_font = self._texture_fonts[font.name]

        texture_coordinates = textures_font.glyph(glyph_index, magnification)
        self._logger.info("{}".format(texture_coordinates))

        # Fixme: wrong
        width, height = [sp2mm(x) for x in char_bounding_box.x.length(), char_bounding_box.y.length()]
        self._glyphs[font.name].append(((xg_mm, yg_mm, width, height), texture_coordinates))

        # char_pixmap_item.setOffset(glyph.horizontal_offset, glyph.vertical_offset)
        # char_pixmap_item.translate(xg_mm, yg_mm)
        # char_pixmap_item.scale(glyph.h_scale, glyph.v_scale)

####################################################################################################
# 
# End
# 
####################################################################################################
