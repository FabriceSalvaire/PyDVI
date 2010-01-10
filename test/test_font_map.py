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
#####################################################################################################

#####################################################################################################

import sys

#####################################################################################################

import Kpathsea 

from FontMap import *

#####################################################################################################

from optparse import OptionParser

usage = 'usage: %prog font_name'

parser = OptionParser(usage)

opt, args = parser.parse_args()

if len(args) != 1:
    parser.error("incorrect number of arguments")

font_map = args[0]

font_map_file = Kpathsea.which(font_map, format = 'map')

if font_map_file is None:
    sys.exit(1)

font_map = FontMap(font_map, filename = font_map_file)
  
# font_map.print_summary()

print 'Look-up cmr10'

cmr10_font_map = font_map['cmr10']

cmr10_font_map.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
