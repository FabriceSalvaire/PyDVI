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

#####################################################################################################

from Font import Font
from PkFontParser import PkFontParser

#####################################################################################################

pk_font_parser = PkFontParser()

#####################################################################################################

class PkFont(Font):

    ###############################################

    def __init__(self, name):

        super(PkFont, self).__init__('pk', name)

        pk_font_parser.process_pk_font(self)

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

    def print_summary(self):

        print '''PK File %s

Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design size  %.1f pt
  - Checksum     %u
  - Resolution
   - Horizontal  %.1f dpi
   - Vertical    %.1f dpi
  ''' % (self.name,
         self.pk_id,
         self.comment,
         self.design_size,
         self.checksum,
         self.horizontal_dpi,
         self.vertical_dpi)

#####################################################################################################
#
# End
#
#####################################################################################################

