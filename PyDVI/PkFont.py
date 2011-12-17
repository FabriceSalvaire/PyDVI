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
#  - 17/01/2010 fabrice
#
#####################################################################################################

"""
"""

#####################################################################################################

__all__ = ['PkFont']

#####################################################################################################

import subprocess

#####################################################################################################

from PyDVI.Font import Font, font_types
from PyDVI.PkFontParser import PkFontParser
from PyDVI.Tools.Logging import print_card

#####################################################################################################

class PkFont(Font):

    """ This class implements the Packed Font Type in the Font Manager.

    To create a Packed Font instance use::

      font = PkFont(font_manager, font_id, name)

    where *font_manager* is a :class:`PyDVI.FontManager.FontManager`, *font_id* is the font id
    provided by the Font Manager and *name* is the font name, "cmr10" for example.  The Packed Font
    file is parsed using a :class:`PyDVI.PkFontParser.PkFontParser` isntance.
    """

    font_type = font_types.Pk
    font_type_string = 'TeX Packed Font'
    extension = 'pk'

    ###############################################

    def __init__(self, font_manager, font_id, name):

        super(PkFont, self).__init__(font_manager, font_id, name)
        
        self.glyphs = {}
        PkFontParser.parse(self)

    ###############################################
 
    def __getitem__(self, char_code):
 
        """ Return the :class:`PyDVI.PkGlyph.PkGlyph` instance for the char code *char_code*. """

        return self.glyphs[char_code]

    ###############################################

    def __len__(self):

        """ Return the number of glyphs in the font. """

        return len(self.glyphs)

    ###############################################

    def _find_font(self):

        """ Find the font file location in the system using Kpathsea and build if it is not
        already done.
        """

        super(PkFont, self)._find_font(kpsewhich_options='-mktex=pk')

    ###############################################

    def _set_preambule_data(self,
                            pk_id,
                            comment,
                            design_font_size,
                            checksum,
                            horizontal_dpi,
                            vertical_dpi):

        """ Set the preambule data from the Packed Font Parser. """

        self.pk_id = pk_id
        self.comment = comment
        self.design_font_size = design_font_size
        self.checksum = checksum
        self.horizontal_dpi = horizontal_dpi
        self.vertical_dpi = vertical_dpi

    ###############################################

    def register_glyph(self, glyph):

        self.glyphs[glyph.char_code] = glyph

    ###############################################

    def get_glyph(self, glyph_index, size=None, resolution=None):

        return self.glyphs[glyph_index]

    ###############################################

    def print_summary(self):

        string_format = """
Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design size  %.1f pt
  - Checksum     %u
  - Resolution
   - Horizontal  %.1f dpi
   - Vertical    %.1f dpi """

        message = self.print_header() + string_format % (
            self.pk_id,
            self.comment,
            self.design_font_size,
            self.checksum,
            self.horizontal_dpi,
            self.vertical_dpi,
            )

        print_card(message)

#####################################################################################################
#
# End
#
#####################################################################################################
