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
#   - singleton ?
#   - font plugin ?
#   - font cache
#
#####################################################################################################

#####################################################################################################

import subprocess
import string

#####################################################################################################

from PkFont import PkFont

#####################################################################################################

font_types = EnumFactory('FontTypes', ('Pk', 'Type1', 'TrueType', 'OpenType'))

class FontManager(object):

    ###############################################

    def __init__(self):

        self.fonts = {}

        self.font_classes = [None]*len(font_types)

        self.font_classes[font_types.Pk] = PkFont

    ###############################################

    def get_font_class(self, font_type):

        return self.font_classes[font_type]
             
    ###############################################

    def load_font(self, font_type, font_name):

        print 'Font Manager load font %s of type %s' % (font_type, font_name)

        return self.get_font_class(font_type)(font_name)

    ###############################################

    def unload_font(self, font_name):

        pass

#####################################################################################################
#
#                                               Test
#
#####################################################################################################
        
if __name__ == '__main__':

    import pylab as pl

    font_manager = FontManager()

    cmr10 = font_manager.load_font(font_types.Pk, 'cmr10')

    cmr10.print_summary()

    glyph = cmr10.get_glyph(ord('x'))

    glyph.print_summary()
    glyph.print_glyph()
    
    glyph_bitmap = glyph.get_glyph_bitmap()
    
    pl.imshow(glyph_bitmap)
    pl.show()

#####################################################################################################
#
# End
#
#####################################################################################################
