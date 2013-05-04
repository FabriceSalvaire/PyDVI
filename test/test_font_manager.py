####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
#
####################################################################################################

####################################################################################################

from PyDVI.Font import *
from PyDVI.FontManager import *

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
