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

__all__ = ['FontManager', 'font_types']

#####################################################################################################

import subprocess
import string

#####################################################################################################

import Kpathsea 

from EnumFactory import *
from FontMap import *
from PkFont import PkFont
from TfmParser import *
from Type1Font import Type1Font

#####################################################################################################

def get_filename_extension(filename):

    index = string.rfind(filename, '.')
        
    if index >= 0:
        index += 1
        if index < len(filename):
            return filename[index:]
    
    return None

#####################################################################################################

font_types = EnumFactory('FontTypes', ('Pk', 'Type1', 'TrueType', 'OpenType'))

#####################################################################################################

class FontManager(object):

    ###############################################

    def __init__(self, font_map):

        self.fonts = {}

        self.font_classes = [None]*len(font_types)

        self.font_classes[font_types.Pk] = PkFont
        self.font_classes[font_types.Type1] = Type1Font

        self.load_font_map(font_map)

        self.tfm_parser = TfmParser()

    ###############################################

    def load_font_map(self, font_map):

        font_map_file = Kpathsea.which(font_map, format = 'map')

        if font_map_file is not None:
            self.font_map = FontMap(font_map, filename = font_map_file)
        else:
            raise NameError('Font Map %s not found' % (font_map)) 

    ###############################################

    def get_font_class(self, font_type):

        return self.font_classes[font_type]

    ###############################################

    def get_font_class_by_filename(self, filename):

        extension = get_filename_extension(filename)

        if extension is not None:
                
            for font_class in self.font_classes:
                if font_class.extension == extension:
                    return font_class

        return None
             
    ###############################################

    def load_font(self, font_type, font_name):

        # Fixme: str(font_type)

        print 'Font Manager load font %s of type %s' % (font_type, font_name)

        return self.get_font_class(font_type)(self, font_name)

    ###############################################

    def load_mapped_font(self, tex_font_name):

        if self.font_map is not None:

            print 'Font Manager load mapped font %s' % (tex_font_name)

            font_map_entry = self.font_map[tex_font_name]

            if font_map_entry is not None:
                font_map_entry.print_summary()

                font_class = self.get_font_class_by_filename(font_map_entry.filename)

                if font_class is not None:
                    return font_class(self, font_map_entry.filename)
                else:
                    raise NameError('Font %s not found' % (tex_font_name))                    

#####################################################################################################
#
# End
#
#####################################################################################################
