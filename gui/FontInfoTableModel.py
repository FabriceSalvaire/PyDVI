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

__ALL__ = ['FontInfoTableModel']

#####################################################################################################

from InfoTableModel import *

#####################################################################################################

class FontInfoTableModel(InfoTableModel):

    #############################################################################

    def __init__(self):

        super(FontInfoTableModel, self).__init__()

        self.font = None

    #############################################################################

    def set_font(self, font):

        self.font = font
        tfm = font.tfm

        self.fields = [
            'Font Name',
            'Smallest Character Code',
            'Largest Character Code',
            'Checksum',
            'Design Font Size',
            'Character Coding Scheme',
            'Family',
            ]

        self.values['Font Name'] = font.name

        self.values['Smallest Character Code'] = tfm.smallest_character_code
        self.values['Largest Character Code'] = tfm.largest_character_code
        self.values['Checksum'] = tfm.checksum
        self.values['Design Font Size'] = tfm.design_font_size
        self.values['Character Coding Scheme'] = tfm.character_coding_scheme
        self.values['Family'] = tfm.family

        self.reset()

#####################################################################################################
#
# End
#
#####################################################################################################
