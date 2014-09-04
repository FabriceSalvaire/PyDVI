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

__ALL__ = ['FontInfoTableModel']

####################################################################################################

from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.Type1Font import Type1Font
from PyDvi.TeXUnit import *

from .InfoTableModel import InfoTableModel

####################################################################################################

def format_dpi(x):
    return '%.1f dpi' % (x)

####################################################################################################

class FontInfoTableModel(InfoTableModel):

    ############################################################################

    def __init__(self):

        super(FontInfoTableModel, self).__init__()

        self.font = None

    ############################################################################

    def set_font(self, font):

        self.font = font
        tfm = font.tfm

        self.fields = [
            'Font Name',
            'Font Type',
            ]

        self.values['Font Name'] = font.name
        self.values['Font Type'] = font.font_type_string

        if isinstance(font, PkFont):

            self.fields += [
            'Comment',
            'Checksum',
            'Design Size',
            'Character Coding Scheme',
            'Family',
            'Horizontal Resolution',
            'Vertical Resolution',
            'Smallest Character Code',
            'Largest Character Code',
            ]

            self.values['Comment'] = font.comment
            self.values['Horizontal Resolution'] = format_dpi(font.horizontal_dpi)
            self.values['Vertical Resolution'] = format_dpi(font.vertical_dpi)
            
            self.values['Checksum'] = tfm.checksum
            self.values['Design Size'] = '%.1f pt %.1f mm' % (tfm.design_font_size, pt2mm(tfm.design_font_size))
            self.values['Character Coding Scheme'] = tfm.character_coding_scheme
            self.values['Family'] = tfm.family
            self.values['Smallest Character Code'] = tfm.smallest_character_code
            self.values['Largest Character Code'] = tfm.largest_character_code

        self.reset()

####################################################################################################
#
# End
#
####################################################################################################
