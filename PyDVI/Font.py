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
#  - 10/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['Font']

#####################################################################################################

from Kpathsea import kpsewhich
from Logging import print_card

#####################################################################################################

class Font(object):

    font_type_string = None
    extension = None

    ###############################################

    def __init__(self, font_manager, font_id, name):

        self.font_manager = font_manager
        self.id = font_id
        self.name = name.replace('.' + self.extension, '')

        ##################
        #
        # Find Font
        #

        relative_filename = self.relative_filename()

        self.filename = kpsewhich(relative_filename)

        if self.filename is None:
            raise NameError("Font file %s not found" % (relative_filename))

        ##################
        #
        # Load TFM
        #

        # Fixme: cache in font manager?

        tfm_file = kpsewhich(self.name, file_format = 'tfm')

        if tfm_file is None:
            raise NameError("TFM file %s not found" % (self.name))

        self.tfm = self.font_manager.tfm_parser.parse(self.name, tfm_file)

    ###############################################

    def relative_filename(self):

        return self.name + '.' + self.extension

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
