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

__all__ = ['VirtualFont']

####################################################################################################

from ..Tools.Logging import print_card
from .Font import Font, font_types
from .VirtualFontParser import VirtualFontParser

####################################################################################################

class VirtualCharacter(object):

    ##############################################

    def __init__(self, char_code, tfm, dvi):

        self.char_code = char_code
        self.tfm = tfm
        self.dvi = dvi

####################################################################################################

class VirtualFont(Font):

    """This class implements the virtual font type in the font manager. """

    font_type = font_types.Vf
    font_type_string = 'TeX Virtual Font'
    extension = 'vf'

    ##############################################

    def __init__(self, font_manager, font_id, name):

        super(VirtualFont, self).__init__(font_manager, font_id, name)

        self.dvi_fonts = {}
        self.first_font = None
        self.fonts = {}
        self.font_id_map = {}
        self._characters = {}
        VirtualFontParser.parse(self)

    ##############################################
 
    def __getitem__(self, char_code):
 
        # """ Return the :class:`PyDvi.PkGlyph.PkGlyph` instance for the char code *char_code*. """

        return self._characters[char_code]

    ##############################################

    def __len__(self):

        """ Return the number of characters in the font. """

        return len(self._characters)

    ##############################################

    def _set_preambule_data(self,
                            vf_id,
                            comment,
                            design_font_size,
                            checksum):

        """ Set the preambule data from the Virtual Font Parser. """

        self.vf_id = vf_id
        self.comment = comment
        self.design_font_size = design_font_size
        self.checksum = checksum

    ##############################################
        
    def register_font(self, font):

        """ Register a :class:`DviFont` instance. """

        if font.id not in self.dvi_fonts:
            self.dvi_fonts[font.id] = font
        if self.first_font is None:
            self.first_font = font.id
        # else:
        #     print 'Font ID %u already registered' % (font.id)

    ##############################################

    def register_character(self, character):

        self._characters[character.char_code] = character

    ##############################################

    def print_summary(self):

        string_format = """
Preambule
  - Vf ID        %u
  - Comment      '%s'
  - Design size  %.1f pt
  - Checksum     %u
"""

        message = self.print_header() + string_format % (
            self.vf_id,
            self.comment,
            self.design_font_size,
            self.checksum,
            )

        print_card(message)

    ##############################################

    def load_dvi_fonts(self):

        self.fonts = {font_id:self.font_manager[dvi_font.name]
                      for font_id, dvi_font in self.dvi_fonts.iteritems()}

    ##############################################

    def update_font_id_map(self):

        self.font_id_map = {font_id:font.global_id
                            for font_id, font in self.fonts.iteritems()}

####################################################################################################
#
# End
#
####################################################################################################
