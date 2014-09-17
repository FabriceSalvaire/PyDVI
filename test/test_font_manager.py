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
#
####################################################################################################

####################################################################################################

from PyDvi.Font.Font import *
from PyDvi.Font.FontManager import *

####################################################################################################
#
# Pk Font
#

def font_manager_pk():

    font_manager = FontManager(font_map='pdftex', use_pk=True)
    cmr10_pk = font_manager._load_font(font_types.Pk, 'cmr10')
    cmr10_pk.print_summary()
    
    glyph = cmr10_pk[ord('x')]
    glyph.print_summary()
    glyph.print_glyph()
    glyph_bitmap = glyph.get_glyph_bitmap()
    cmr10_pk.tfm[ord('A')].print_summary()

####################################################################################################
#
# Type1 Font
#

font_manager = FontManager(font_map='pdftex', use_pk=False)
cmr10_type1 = font_manager['cmr10']
cmr10_type1.print_summary()

### #cmr10_type1.print_glyph_table()
### 
### cmr10_type1.tfm[ord('A')].print_summary()

####################################################################################################
#
# End
#
####################################################################################################
