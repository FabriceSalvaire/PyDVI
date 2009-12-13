#####################################################################################################

import subprocess
import string

#####################################################################################################

from PkFont import PkFont

#####################################################################################################

# Singleton
# Font plugin ?

class FontManager(object):

    # Enum
    Pk, Type1, TrueType, OpenType, NumberOfFontClasses = range(5)

    ###############################################

    def __init__(self):

        self.fonts = {}

        self.font_classes = [None]*self.NumberOfFontClasses

        self.font_classes[self.Pk] = PkFont

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

    cmr10 = font_manager.load_font(FontManager.Pk, 'cmr10')

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
