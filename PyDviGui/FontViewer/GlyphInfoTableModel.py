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

__all__ = ['GlyphInfoTableModel']

####################################################################################################

from PyDvi.TeXUnit import *

from .InfoTableModel import InfoTableModel

####################################################################################################

class GlyphInfoTableModel(InfoTableModel):

    ############################################################################

    def __init__(self):

        super(GlyphInfoTableModel, self).__init__()

        self.tfm_char = None

    ############################################################################

    def format_dimension(self, x):

        return '%.2f ds %.2f mm' % (x, pt2mm(int(x*self.design_font_size)))

    ############################################################################

    def set_tfm_char(self, tfm_char):

        self.tfm_char = tfm_char

        self.fields = [
            'Width',
            'Height',
            'Depth',
            'Italic Correction',
            ]

        self.design_font_size = tfm_char.tfm.design_font_size

        self.values['Width'] = self.format_dimension(tfm_char.width)
        self.values['Height'] = self.format_dimension(tfm_char.height)
        self.values['Depth'] = self.format_dimension(tfm_char.depth)
        self.values['Italic Correction'] = self.format_dimension(tfm_char.italic_correction)

        self.reset()

####################################################################################################
#
# End
#
####################################################################################################
