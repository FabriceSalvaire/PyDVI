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
#  - 11/10/2011 fabrice
#
####################################################################################################

####################################################################################################

import argparse
import sys

####################################################################################################

from PyDVI.FontMap import *
from PyDVI.Kpathsea import kpsewhich

####################################################################################################

parser = argparse.ArgumentParser(description='Test Font Map.')
parser.add_argument('font_map', metavar='FontMap',
                    help='TeX font map, e.g. pdftex')
args = parser.parse_args()

####################################################################################################

font_map_file = kpsewhich(args.font_map, file_format='map')

if font_map_file is None:
    print 'Font map %s not found' % (args.font_map)
    sys.exit(1)

font_map = FontMap(font_map_file)
font_map.print_summary()

print '\nLook-up cmr10'
cmr10_font_map = font_map['cmr10']
cmr10_font_map.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
