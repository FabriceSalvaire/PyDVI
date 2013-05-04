# -*- coding: utf-8 -*-

####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
# - 10/12/2011
#
####################################################################################################

####################################################################################################

__all__ = ['GlyphInfoTableModel']

####################################################################################################

from PyDVI.TeXUnit import *

from InfoTableModel import InfoTableModel

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
