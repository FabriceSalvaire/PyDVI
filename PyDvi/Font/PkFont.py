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

__all__ = ['PkFont']

####################################################################################################

from ..Tools.Logging import print_card
from .Font import Font, font_types
from .PkFontParser import PkFontParser

####################################################################################################

class PkFont(Font):

    """This class implements the packed font type in the font manager.

    To create a packed font instance use::

      font = PkFont(font_manager, font_id, name)

    where *font_manager* is a :class:`PyDvi.FontManager.FontManager` instance, *font_id* is the font
    id provided by the font manager and *name* is the font name, "cmr10" for example.  The packed
    font file is parsed using a :class:`PyDvi.PkFontParser.PkFontParser` instance.

    """

    font_type = font_types.Pk
    font_type_string = 'TeX Packed Font'
    extension = 'pk'

    ##############################################

    def __init__(self, font_manager, font_id, name):

        super(PkFont, self).__init__(font_manager, font_id, name)
        
        self._glyphs = {}
        PkFontParser.parse(self)

    ##############################################
 
    def __getitem__(self, char_code):
 
        """ Return the :class:`PyDvi.PkGlyph.PkGlyph` instance for the char code *char_code*. """

        return self._glyphs[char_code]

    ##############################################

    def __len__(self):

        """ Return the number of glyphs in the font. """

        return len(self._glyphs)

    ##############################################

    def _find_font(self):

        """ Find the font file location in the system using Kpathsea and build if it is not
        already done.
        """

        super(PkFont, self)._find_font(kpsewhich_options='-mktex=pk')

    ##############################################

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

    ##############################################

    def register_glyph(self, glyph):

        self._glyphs[glyph.char_code] = glyph

    ##############################################

    def get_glyph(self, glyph_index, size=None, resolution=None):

        return self._glyphs[glyph_index]

    ##############################################

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

####################################################################################################
#
# End
#
####################################################################################################
