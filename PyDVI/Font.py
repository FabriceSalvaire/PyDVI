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
#
#####################################################################################################

#####################################################################################################

__all__ = ['Font']

#####################################################################################################

import subprocess
import string

#####################################################################################################

import Kpathsea

from Logging import *

#####################################################################################################

class Font(object):

    ###############################################

    def __init__(self, font_manager, id, name):

        self.font_manager = font_manager
        self.id = id

        self.name = string.replace(name, '.' + self.extension, '')

        self.find_font()

        self.load_tfm()

    ###############################################

    def relative_filename(self):

        return self.name + '.' + self.extension

    ###############################################

    def find_font(self):

        relative_filename = self.relative_filename()

        self.filename = Kpathsea.which(relative_filename)

        if self.filename is None:
            raise NameError("Font file %s not found" % (relative_filename))

    ###############################################

    def load_tfm(self):

        # Fixme: cache in font manager?

        tfm_file = Kpathsea.which(self.name, format = 'tfm')

        if tfm_file is None:
            raise NameError("TFM file %s not found" % (self.name))

        self.tfm = self.font_manager.tfm_parser.parse(self.name, tfm_file)
        
        # self.tfm.print_summary()

    ###############################################

    def print_header(self):

        return '''%s %s

 - font file: %s
 - tfm  file: %s
''' % (self.font_type_string,
       self.name,
       self.filename,
       self.tfm.filename,
       )

    ###############################################

    def print_summary(self):

        print_card(self.print_header())

#####################################################################################################
#
# End
#
#####################################################################################################
