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

from PIL import Image, ImageDraw

####################################################################################################

from PyDvi.Dvi.DviMachine import DviSimplifyMachine
from PyDvi.TeXUnit import *
from PyDvi.Tools.Interval import Interval2D

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

    def begin_run_page(self, png_path, dpi, tight=False):

        self._png_path = png_path
        self._dpi = dpi
        self._tight = tight

        self._sp_to_px = self._dpi * sp2in(1)

        program = self.current_opcode_program

        width = program.width
        height = program.height
        if not width or not height: 
            first_page = self.dvi_program[0]
            width, height = first_page.width, first_page.height
        if not width or not height:
            self._logger.warning('Page size is null')
            width, height = 210, 297 # use A4

        width_px = self.mm2px(width)
        height_px = self.mm2px(height)

        self._logger.info("Image dimension (width, height) = ({},{})".format(width_px, height_px))

        self._image = Image.new('RGB', (width_px, height_px), color=(255, 255, 255))
        self._draw = ImageDraw.Draw(self._image)

        self._bounding_box = None

    ##############################################

    def end_run_page(self):

        if self._tight:
            image = self._image.crop(self._bounding_box.bounding_box())
        else:
            image = self._image
        image.save(self._png_path)

    ##############################################

    def mm2px(self, x):
        return rint(mm2in(x)*self._dpi)

    ##############################################

    def sp2px(self, x):
        return rint(self._sp_to_px * x)

    ##############################################
    
    def paint_rule(self, x, y, w, h):

        # self._logger.info("\nrule ({}, {}) +({}, {})".format(x, y, w, h))
        x0, y0, x1, y1 = [self.sp2px(x) for x in (x, y - h, x + w, y)]
        self._draw.rectangle((x0, y0, x1, y1),
                             fill=self.current_colour.colour)

        rule_bounding_box = Interval2D([x0, x1], [y0, y1])
        if self._bounding_box is None:
            self._bounding_box = rule_bounding_box
        else:
            self._bounding_box |= rule_bounding_box

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
        glyph_bitmap = 255 - glyph.glyph_bitmap # inverse: paint black on white
        height, width = glyph_bitmap.shape[:2] # depth

        x = self.sp2px(xg) + glyph.offset[0]
        y = self.sp2px(yg) + glyph.size[1] - glyph.offset[1] # offset = top - origin

        x0, y0, x1, y1 = [x, y - height, x + width, y]

        glyph_image = Image.fromarray(glyph_bitmap)
        self._image.paste(glyph_image, (x0, y0, x1, y1))

        char_bounding_box = Interval2D([x0, x1], [y0, y1])
        if self._bounding_box is None:
            self._bounding_box = char_bounding_box
        else:
            self._bounding_box |= char_bounding_box

####################################################################################################
# 
# End
# 
####################################################################################################
