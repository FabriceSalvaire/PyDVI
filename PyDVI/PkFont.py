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

__ALL__ = ['PkFont']

#####################################################################################################

import subprocess

#####################################################################################################

from Font import *
from Logging import *

#####################################################################################################

class PkFont(Font):

    font_type_string = 'TeX Packed Font'
    extension = 'pk'

    ###############################################

    def __init__(self, font_manager, id, name):

        super(PkFont, self).__init__(font_manager, id, name)
        
        self.glyphs = {}

        self.font_manager.pk_font_parser.process_pk_font(self)

    ###############################################
 
    def __getitem__(self, char_code):
 
        return self.glyphs[char_code]

    ###############################################

    def __len__(self):

        return len(self.glyphs)

    ###############################################

    def make_pk(self):

        # --destdir

        process = subprocess.Popen(string.join(('mktexpk', self.name), sep = ' '), shell=True)

    ###############################################

    def set_preambule_data(self,
                           pk_id,
                           comment,
                           design_size,
                           checksum,
                           horizontal_dpi,
                           vertical_dpi):

        self.pk_id = pk_id
        self.comment = comment
        self.design_size = design_size
        self.checksum = checksum
        self.horizontal_dpi = horizontal_dpi
        self.vertical_dpi = vertical_dpi

    ###############################################

    def register_glyph(self, glyph):

        self.glyphs[glyph.char_code] = glyph

    ###############################################

    def get_glyph(self, glyph_index, size = None, resolution = None):

        return self.glyphs[glyph_index]

    ###############################################

    def print_summary(self):

        print_card (self.print_header() + 
                    '''
Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design size  %.1f pt
  - Checksum     %u
  - Resolution
   - Horizontal  %.1f dpi
   - Vertical    %.1f dpi ''' % (
                self.pk_id,
                self.comment,
                self.design_size,
                self.checksum,
                self.horizontal_dpi,
                self.vertical_dpi,
                ))

#####################################################################################################
#
# End
#
#####################################################################################################
