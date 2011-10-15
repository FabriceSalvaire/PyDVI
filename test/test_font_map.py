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
#  - 11/10/2011 fabrice
#
#####################################################################################################

#####################################################################################################

import sys

#####################################################################################################

from PyDVI.FontMap import *
from PyDVI.Kpathsea import kpsewhich

#####################################################################################################

from optparse import OptionParser

usage = 'usage: %prog font_map'

parser = OptionParser(usage)

opt, args = parser.parse_args()

if len(args) != 1:
    parser.error("Give a TeX font map, e.g. pdftex")

font_map = args[0]

font_map_file = kpsewhich(font_map, file_format='map')

if font_map_file is None:
    print 'Font map %s not found' % (font_map_file)
    sys.exit(1)

font_map = FontMap(font_map, filename=font_map_file)
  
font_map.print_summary()

print 'Look-up cmr10'
cmr10_font_map = font_map['cmr10']
cmr10_font_map.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
