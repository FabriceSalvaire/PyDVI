# -*- coding: utf-8 -*-

####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

__ALL__ = ['FontInfoTableModel']

####################################################################################################

from PyDVI.PkFont import PkFont
from PyDVI.TeXUnit import *
from PyDVI.Type1Font import Type1Font

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
