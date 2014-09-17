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
#                                              Audit
#
# - 13/11/2011 Fabrice
#   x
#
####################################################################################################

####################################################################################################

import argparse
import sys

####################################################################################################

from PyDvi.Font.Encoding import Encoding
from PyDvi.Kpathsea import kpsewhich

####################################################################################################

parser = argparse.ArgumentParser(description='Test Encoding.')
parser.add_argument('encoding', metavar='Encoding',
                    help='TeX encoding, e.g. cork')
args = parser.parse_args()

####################################################################################################

encoding_file = kpsewhich(args.encoding, file_format='enc files')

if encoding_file is None:
    print 'Encoding %s not found' % (args.encoding)
    sys.exit(1)

print 'Read %s encoding file' % (encoding_file)

encoding = Encoding(encoding_file)
encoding.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
