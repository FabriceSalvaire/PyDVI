####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2011 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
####################################################################################################

####################################################################################################

import argparse
import logging
import sys

####################################################################################################

from PyDVI.Kpathsea import kpsewhich
from PyDVI.PkFont import PkFont
from PyDVI.PkFontParser import PkFontParser

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

parser = argparse.ArgumentParser(description='Test PK Font.')
parser.add_argument('font', metavar='Font',
                    help='Font name, e.g. cmr10')
args = parser.parse_args()

####################################################################################################

pk_file = kpsewhich(args.font, file_format='pk', options='-mode nextscrn -dpi 100 -mktex=pk')
if pk_file is None:
    print 'PK file %s not found' % (args.font)
    sys.exit(1)

pk_font = PkFont(font_manager=None, font_id=0, name=args.font)
PkFontParser.parse(pk_font)

####################################################################################################
#
# End
#
####################################################################################################
