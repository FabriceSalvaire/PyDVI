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

from PIL import Image, ImageDraw

####################################################################################################

from PyDvi.Dvi.DviMachine import DviMachine, DviSimplifyMachine
from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.Type1Font import Type1Font
from PyDvi.TeXUnit import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def rint(f):
    return int(round(f))

####################################################################################################

class ImageDviMachine(DviSimplifyMachine):

    _logger = _module_logger.getChild('ImageDviMachine')
    
    ##############################################

    def __init__(self, font_manager):

        super(ImageDviMachine, self).__init__(font_manager)

    ##############################################

    def begin_run_page(self, png_path, dpi):

        self._dpi = dpi
        self._png_path = png_path

        program = self.current_opcode_program

        width = program.width
        height = program.height
        if not width or not height: 
            first_page = self.dvi_program[0]
            width, height = first_page.width, first_page.height
        if not width or not height:
            self._logger.warning('Page size is null')
            width, height = 210, 297 # use A4

        width_px = self.mm_to_px(width)
        height_px = self.mm_to_px(height)

        self._logger.info("Image dimension (width, height) = ({},{})".format(width_px, height_px))

        self._image = Image.new('RGB', (width_px, height_px), color=(255, 255, 255))
        self._draw = ImageDraw.Draw(self._image)

    ##############################################

    def end_run_page(self):

        self._image.save(self._png_path)

    ##############################################

    def mm_to_px(self, x):
        # Fixme: better unit ?
        return rint(mm2in(x)*self._dpi)

    ##############################################
    
    def paint_rule(self, x, y, w, h):

        # self._logger.info("\nrule ({}, {}) +({}, {})".format(x, y, w, h))
        x_mm, y_mm, w_mm, h_mm = [sp2mm(z) for z in (x, y, w, h)]
        
        self._draw.rectangle([self.mm_to_px(x) for x in (x_mm, y_mm - h_mm, x_mm + w_mm, y_mm)],
                             fill=self.current_colour.colour)

    ##############################################

    def paint_char(self, xg, yg, char_bounding_box, font, dvi_font, glyph_index):

        if dvi_font.global_id is not None:
            font_id = dvi_font.global_id
        else:
            font_id = dvi_font.id

        # self._logger.info("\nchar ({}, {}) {} {}[{}]@{}".format(xg, yg, char_bounding_box,
        #                                                         font.name, glyph_index, dvi_font.magnification))

        # if font.tfm is not None:
        #     size = dvi_font.magnification * font.tfm.design_font_size # pt
        # else:
        size = dvi_font.magnification * sp2pt(dvi_font.design_size) # pt

        glyph = font.get_glyph(glyph_index, size, resolution=self._dpi)
        glyph_bitmap = -(glyph.glyph_bitmap - 255)
        height_px, width_px = glyph_bitmap.shape[:2] # depth

        xg_mm = sp2mm(xg) + glyph.px_to_mm(glyph.offset[0])
        yg_mm = sp2mm(yg) + glyph.px_to_mm(glyph.size[1] - glyph.offset[1]) # offset = top - origin
        # width = glyph.px_to_mm(glyph.size[0])
        # height = glyph.px_to_mm(glyph.size[1])

        x_px = self.mm_to_px(xg_mm)
        y_px = self.mm_to_px(yg_mm)

        glyph_image = Image.fromarray(glyph_bitmap)
        self._image.paste(glyph_image, [x_px, y_px - height_px, x_px + width_px, y_px])

        # x_mm = sp2mm(char_bounding_box.x.inf)
        # y_mm = sp2mm(char_bounding_box.y.inf)
        # box_width  = sp2mm(char_bounding_box.x.length())
        # box_height = sp2mm(char_bounding_box.y.length())
        # y_mm -= box_height

        # glyph_index = self._glyph_indexes[font_id]
        # positions, bounding_boxes, texture_coordinates, colours = self.glyphs[font_id]
        # positions[glyph_index] = xg_mm, yg_mm, width, height
        # bounding_boxes[glyph_index] = x_mm, y_mm, box_width, box_height
        # texture_coordinates[glyph_index] = glyph.texture_coordinates
        # colours[glyph_index] = self.current_colour.colour

####################################################################################################
# 
# End
# 
####################################################################################################
