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
                           horizontal_pixels_per_point,
                           vertical_pixels_per_point):

        self.pk_id = pk_id
        self.comment = comment
        self.design_size = design_size
        self.checksum = checksum
        self.horizontal_pixels_per_point = horizontal_pixels_per_point
        self.vertical_pixels_per_point = vertical_pixels_per_point

    ###############################################

    def print_summary(self):

        print '''PK File %s

Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design Size  %.1f pt
  - Checksum     %u
  - Horizontal Resolution %.1f dpi
  - Vertical   Resolution %.1f dpi
  ''' % (self.name,
         self.pk_id,
         self.comment,
         self.design_size,
         self.checksum,
         self.horizontal_pixels_per_point,
         self.vertical_pixels_per_point)

#####################################################################################################
#
# End
#
#####################################################################################################

