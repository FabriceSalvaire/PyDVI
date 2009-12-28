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
#  - 19/12/2009 fabrice
#
#####################################################################################################

#####################################################################################################

import subprocess
import string

#####################################################################################################

import Kpathsea

#####################################################################################################

class Font(object):

    ###############################################

    def __init__(self, font_manager, name):

        self.font_manager = font_manager

        self.name = name

        self.glyphs = {}

        self.find_font()

        self.load_tfm()

        # if self.file_name is None:
        #     self.make_pk()

    ###############################################

    def __getitem__(self, char_code):

        return self.glyphs[char_code]

    ###############################################

    def __len__(self):

        return len(self.glyphs)

    ###############################################

    def relative_filename(self):

        return self.name + '.' + self.extension

    ###############################################

    def find_font(self):

        relative_filename = self.relative_filename()

        self.filename = Kpathsea.which(relative_filename)

        if self.filename is None:
            raise NameError('Font not found' % (relative_filename))

    ###############################################

    def load_tfm(self):

        # Fixme: cache in font manager?

        tfm_file = Kpathsea.which(self.name, format = 'tfm')

        if tfm_file is None:
            raise NameError('TFM %s not found' % (self.name))

        self.tfm = self.font_manager.tfm_parser.parse(self.name, tfm_file)
        
        # self.tfm.print_summary()

    ###############################################

    def register_glyph(self, glyph):

        self.glyphs[glyph.char_code] = glyph

#####################################################################################################
#
# End
#
#####################################################################################################
