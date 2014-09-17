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
####################################################################################################

####################################################################################################

import argparse
import logging
import sys

####################################################################################################

from PyDvi.Kpathsea import kpsewhich
from PyDvi.Font.PkFont import PkFont
from PyDvi.Font.PkFontParser import PkFontParser

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

####################################################################################################
#
# End
#
####################################################################################################
