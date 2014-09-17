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

import argparse
import logging
import sys

####################################################################################################

from PyDvi.Font.VirtualFont import VirtualFont
from PyDvi.Kpathsea import kpsewhich

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

parser = argparse.ArgumentParser(description='Test Virtual Font.')
parser.add_argument('font', metavar='VirtualFont',
                    help='Font name, e.g. phvr7t')
args = parser.parse_args()

####################################################################################################

vf_file = kpsewhich(args.font, file_format='vf')
if vf_file is None:
    print 'VF file %s not found' % (args.font)
    sys.exit(1)

vf_font = VirtualFont(font_manager=None, font_id=0, name=args.font)
vf_font.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
