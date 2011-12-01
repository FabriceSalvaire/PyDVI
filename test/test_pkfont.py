#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2011 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
#####################################################################################################

#####################################################################################################

import logging
import sys

from optparse import OptionParser

#####################################################################################################

from PyDVI.Kpathsea import kpsewhich
from PyDVI.PkFont import PkFont
from PyDVI.PkFontParser import PkFontParser

#####################################################################################################

logging.basicConfig(level=logging.DEBUG)

#####################################################################################################

usage = 'usage: %prog font_name'

parser = OptionParser(usage)

opt, args = parser.parse_args()

if len(args) != 1:
    parser.error("Give a a font name, e.g. cmr10")

font_name = args[0]

#####################################################################################################

pk_file = kpsewhich(font_name, file_format='pk', options='-mode nextscrn -dpi 100 -mktex=pk')
if pk_file is None:
    print 'PK file %s not found' % (font_name)
    sys.exit(1)

pk_font_parser = PkFontParser()

pk_font = PkFont(font_manager=None, font_id=0, name=font_name)
pk_font_parser.process_pk_font(pk_font)

#####################################################################################################
#
# End
#
#####################################################################################################
