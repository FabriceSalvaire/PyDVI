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
#
# Audit
#
# - 10/12/2011 fabrice
#   - singleton ?
#   - font plugin ?
#   - font cache
#
####################################################################################################

""" This module provides a Font Manager for the DVI Machine.

Each time a font is loaded, the Font Manager attributes to it an incremental identification number
that corresponds to the font index in the DVI Machine.

The different type of fonts (Packed, Type 1, etc.) are handled by a subclass of
:class:`PyDvi.Font.Font` that provide a kind of plugin mechanism.  In order to manage the mapping
between the TeX font name and the Type 1 font name, the Font Manager constructor takes a Font Map
name as parameter.

To create a Font Manager instance using the "pdftex" Font Map do::

  font_manager = FontManager('pdftex')

Then to load for example the font "cmr10" and get the font class instance do::

  font = font_manager["cmr10"]

Latter the same piece of codes could be use to retrieve the font class instance.

To get the number of fonts in the Font Manager use the :func:`len` function::

  len(font_manager)

"""

####################################################################################################

__all__ = ['FontManager']

####################################################################################################

import logging

####################################################################################################

from ..Kpathsea import kpsewhich
from ..Tools.FuncTools import get_filename_extension
from .Font import font_types, sort_font_class
from .FontMap import FontMap
from .PkFont import PkFont
from .Type1Font import Type1Font

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class FontManager(object):

    """ This class implements a Font Manager for the DVI Machine.
    """

    font_classes = sort_font_class(PkFont,
                                   Type1Font,
                                   )

    extension_to_font_class = {x.extension:x for x in font_classes}

    ##############################################

    def __init__(self, font_map, use_pk=False):

        """ The Font Map name is provided by *font_map*.
        """

        self.use_pk = use_pk

        self.fonts = {}
        self.last_font_id = 0

        self._init_font_map(font_map)

    ##############################################

    def _init_font_map(self, font_map):

        """ Load the font map.
        """

        font_map_file = kpsewhich(font_map, file_format='map')
        if font_map_file is not None:
            self.font_map = FontMap(font_map_file)
        else:
            raise NameError("Font Map %s not found" % (font_map)) 

    ##############################################

    def __contains__(self, font_name):

        """ Return :obj:`True` if the Font Manager holds the font *font_name*. """

        return font_name in self.fonts

    ##############################################

    def __getitem__(self, font_name):

        """ Return the font *font_name* instance.  If the font is not in the Font Manager then load
        it.
        """

        if font_name in self:
            font = self.fonts[font_name]
        else:
            if self.use_pk:
                font = self._load_font(font_types.Pk, font_name)
            else:
                font = self.fonts[font_name] = self.load_mapped_font(font_name)

        return font

    ##############################################

    def _get_new_font_id(self):

        """ Return a new font id.
        """

        self.last_font_id += 1

        return self.last_font_id

    ##############################################

    def _load_font(self, font_type, font_name):

        """ Load the font *font_name* with the font type *font_type* plugin.
        """

        font_class = self.font_classes[font_type]
        return font_class(self, self._get_new_font_id(), font_name)

    ##############################################
  
    def get_font_class_by_filename(self, filename):
  
        return self.extension_to_font_class[get_filename_extension(filename)]
  
    ##############################################
  
    def load_mapped_font(self, tex_font_name):
        
        try:
            font_map_entry = self.font_map[tex_font_name]
            font_map_entry.print_summary()
            font_class = self.get_font_class_by_filename(font_map_entry.pfb_filename)
            _module_logger.info("Font %s is mapped to %s" % (tex_font_name, font_map_entry.pfb_filename))
        except:
            raise NameError("Could not found a mapped font for %s" % (tex_font_name))
            # return self.load_font(font_types.Pk, tex_font_name)

        return font_class(self, self._get_new_font_id(), font_map_entry.pfb_filename)

####################################################################################################
#
# End
#
####################################################################################################
