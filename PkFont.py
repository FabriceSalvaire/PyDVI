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

    def __init__(self, font_name):

        super(PkFont, self).__init__('pk', font_name)

        pk_font_parser.process_pk_font(self)

    ###############################################

    def make_pk(self):

        # --destdir

        process = subprocess.Popen(string.join(('mktexpk', self.font_name), sep = ' '), shell=True)

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
  ''' % (self.font_name,
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

