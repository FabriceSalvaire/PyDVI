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

import numpy as np

####################################################################################################

from PyDvi.Dvi.DviMachine import DviMachine, DviSimplifyMachine
from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.Type1Font import Type1Font
from PyDvi.TeXUnit import *

####################################################################################################

from .TextureFont import TextureFont

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlDviMachine(DviSimplifyMachine):

    _logger = _module_logger.getChild('GlDviMachine')
    
    ##############################################

    def __init__(self, font_manager):

        super(GlDviMachine, self).__init__(font_manager)

    ##############################################

    def begin_run_page(self):

        self._texture_fonts = {}
        self._glyphs = {} # index by font name

        self._rule_index = 0
        # rule = [vec2 (x,y) position, vec2 (width,height) dimension, vec4 rgba colour]
        self._rules = np.zeros((self.current_opcode_program.number_of_rules, 8), dtype='f')

    ##############################################

    def paint_rule(self, x, y, w, h):

        self._logger.info("\nrule ({}, {}) +({}, {})".format(x, y, w, h))
        x_mm, y_mm, w_mm, h_mm = [sp2mm(z) for z in (x, y, w, h)]
        y_mm = 297 - y_mm # Fixme: opengl frame

        self._rules[self._rule_index,:4] = [x_mm, y_mm, w_mm, h_mm]
        self._rules[self._rule_index,4:] = self.current_colour.colour
        self._rule_index += 1

    ##############################################

    def paint_char(self, xg, yg, char_bounding_box, font, glyph_index, magnification):

        self._logger.info("\nchar ({}, {}) {} {}[{}]@{}".format(xg, yg, char_bounding_box,
                                                                font.name, glyph_index, magnification))

        if font.name not in self._texture_fonts:
            textures_font = TextureFont(font)
            self._texture_fonts[font.name] = textures_font
            self._glyphs[font.name] = []
        else:
            textures_font = self._texture_fonts[font.name]

        glyph = textures_font.glyph(glyph_index, magnification)

        xg_mm = sp2mm(xg) + glyph.px_to_mm(glyph.offset[0])
        yg_mm = sp2mm(yg) + glyph.px_to_mm(glyph.size[1] - glyph.offset[1]) # offset = top - origin
        yg_mm = 297 - yg_mm # Fixme: opengl frame
        width = glyph.px_to_mm(glyph.size[0])
        height = glyph.px_to_mm(glyph.size[1])

        x_mm = sp2mm(char_bounding_box.x.inf)
        y_mm = sp2mm(char_bounding_box.y.inf)
        y_mm = 297 - y_mm # Fixme: opengl frame
        box_width  = sp2mm(char_bounding_box.x.length())
        box_height = sp2mm(char_bounding_box.y.length())
        y_mm -= box_height

        # Fixme: wrong
        self._glyphs[font.name].append(((xg_mm, yg_mm, width, height),
                                        (x_mm, y_mm, box_width, box_height),
                                        glyph.texture_coordinates))

        # horizontal_offset = -glyph.horizontal_offset
        # vertical_offset = -glyph.vertical_offset
        # h_scale = magnification*dpi2mm(glyph.pk_font.horizontal_dpi)
        # v_scale = magnification*dpi2mm(glyph.pk_font.vertical_dpi)

        # char_pixmap_item.setOffset(glyph.horizontal_offset, glyph.vertical_offset)
        # char_pixmap_item.translate(xg_mm, yg_mm)
        # char_pixmap_item.scale(glyph.h_scale, glyph.v_scale)

####################################################################################################
# 
# End
# 
####################################################################################################
