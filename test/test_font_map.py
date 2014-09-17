####################################################################################################
# 
# PyDvi - A Python Library to Process DVI Stream
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

from PyDvi.Font.FontMap import *
from PyDvi.Kpathsea import kpsewhich

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
