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
#   - singleton ?
#   - font plugin ?
#   - font cache
#
#####################################################################################################

#####################################################################################################

__all__ = ['FontManager', 'font_types']

#####################################################################################################

import subprocess

import ft2

#####################################################################################################

from EnumFactory import EnumFactory
from FontMap import *
from Kpathsea import kpsewhich
from PkFont import PkFont
from PkFontParser import PkFontParser
from TfmParser import *
from Type1Font import *

#####################################################################################################

def get_filename_extension(filename):

    index = filename.rfind('.')
        
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

    def __init__(self, font_map, use_pk=False):

        self.use_pk = use_pk

        self.fonts = {}

        self.last_font_id = 0

        self.font_classes = [None]*len(font_types)

        self.__init_font_map(font_map)
        self.__init_tfm()
        self.__init_pk_font()
        self.__init_freetype()

    ###############################################

    def __init_font_map(self, font_map):

        '''
        Load the font map
        '''

        font_map_file = kpsewhich(font_map, file_format='map')

        if font_map_file is not None:
            self.font_map = FontMap(font_map, filename=font_map_file)
        else:
            raise NameError("Font Map %s not found" % (font_map)) 

    ###############################################

    def __init_tfm(self):

        self.tfm_parser = TfmParser()

    ###############################################

    def __init_pk_font(self):

        self.pk_font_parser = PkFontParser()

        self.font_classes[font_types.Pk] = PkFont

    ###############################################

    def __init_freetype(self):

        try:
            self.freetype_library = ft2.Library()
        except:
            raise NameError("Error loading Freetype")

        self.font_classes[font_types.Type1] = Type1Font

    ###############################################

    def __getitem__(self, tex_font_name):

        if self.is_font_loaded(tex_font_name):
            font = self.fonts[tex_font_name]

        else:
            
            if self.use_pk:
                font = self.load_font(font_types.Pk, tex_font_name)
            else:
                font = self.fonts[tex_font_name] = self.load_mapped_font(tex_font_name)

        return font

    ###############################################

    def get_new_font_id(self):

        self.last_font_id += 1

        return self.last_font_id

    ###############################################

    def set_use_pk(self, value):

        self.use_pk = value

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

    def is_font_loaded(self, font_name):

        return self.fonts.has_key(font_name)
             
    ###############################################

    def load_font(self, font_type, font_name):

        # Fixme: str(font_type)

        font_class = self.get_font_class(font_type)

        print "Font Manager load font %s of type %s" % (font_name, font_class.font_type_string)

        return font_class(self, self.get_new_font_id(), font_name)

    ###############################################

    def load_mapped_font(self, tex_font_name):

        if self.font_map is not None:

            print "Font Manager load mapped font %s" % (tex_font_name)

            font_map_entry = self.font_map[tex_font_name]

            if font_map_entry is not None:

                font_map_entry.print_summary()

                font_class = self.get_font_class_by_filename(font_map_entry.filename)

                if font_class is not None:
                    return font_class(self, self.get_new_font_id(), font_map_entry.filename)
                else:
                    raise NameError("Unknown font class for font %s mapped to %s"
                                    % (tex_font_name,
                                       font_map_entry.filename))
            
            else:
                return self.load_font(font_types.Pk, tex_font_name)

#####################################################################################################
#
# End
#
#####################################################################################################
