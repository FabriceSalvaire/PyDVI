####################################################################################################
# 
# PyDVI - A Python Library to Process DVI Stream
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
#
# Audit
#
# - 11/12/2011 fabrice
#   - print_header ?
#
####################################################################################################

""" This module provides a base class for font type managed by the font manager.
"""

####################################################################################################

__all__ = ['Font', 'font_types', 'sort_font_class']

####################################################################################################

from PyDVI.Kpathsea import kpsewhich
from PyDVI.TfmParser import TfmParser
from PyDVI.Tools.EnumFactory import EnumFactory
from PyDVI.Tools.Logging import print_card

####################################################################################################

#: Font Type Enumerate 
font_types = EnumFactory('FontTypes', ('Pk', 'Type1', 'TrueType', 'OpenType'))

def sort_font_class(*args):
    """ Sort a list of :class:`Font` instance by font type enumerate. """
    return sorted(args, cmp=lambda a, b: cmp(a.font_type, b.font_type))

####################################################################################################

class Font(object):

    """ This class is a base class for font managed by the Font Manager.

    Class attributes to be defined in subclass:

      ``font_type``
        Font Type Enumerate

      ``font_type_string``
        Description string of the font type

      ``extension``
        File extension

    To create a :class:`Font` instance use::

      font = Font(font_manager, font_id, name)

    where *font_manager* is a :class:`PyDVI.FontManager.FontManager`, *font_id* is the font id
    provided by the Font Manager and *name* is the font name, "cmr10" for example.
    """

    font_type = None
    font_type_string = None
    extension = None

    ##############################################

    def __init__(self, font_manager, font_id, name):

        self.font_manager = font_manager
        self.id = font_id
        self.name = name.replace('.' + self.extension, '')

        self._find_font()
        self._find_tfm()

    ##############################################

    def _find_font(self, kpsewhich_options=None):

        """ Find the font file location in the system using Kpathsea. """

        basename = self.basename()

        self.filename = kpsewhich(basename, options=kpsewhich_options)
        if self.filename is None:
            raise NameError("Font file %s not found" % (basename))

    ##############################################

    def _find_tfm(self):

        """ Find the TFM file location in the system using Kpathsea and load it. """

        tfm_file = kpsewhich(self.name, file_format='tfm')
        if tfm_file is None:
            raise NameError("TFM file %s not found" % (self.name))

        self.tfm = TfmParser.parse(self.name, tfm_file)

    ##############################################

    def basename(self):

        """ Return the basename. """

        return self.name + '.' + self.extension

    ##############################################

    def print_header(self):

        string_format = """%s %s

 - font file: %s
 - tfm  file: %s
"""
        
        return  string_format % (self.font_type_string,
                                 self.name,
                                 self.filename,
                                 self.tfm.filename,
                                 )

    ##############################################

    def print_summary(self):

        print_card(self.print_header())

####################################################################################################
#
# End
#
####################################################################################################
