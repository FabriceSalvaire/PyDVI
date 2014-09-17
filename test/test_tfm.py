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
import sys

####################################################################################################

from PyDvi.Font.TfmParser import TfmParser
from PyDvi.Kpathsea import kpsewhich

####################################################################################################

parser = argparse.ArgumentParser(description='Test TFM.')
parser.add_argument('font', metavar='Font',
                    help='Font name, e.g. cmr10')
args = parser.parse_args()

####################################################################################################

tfm_file = kpsewhich(args.font, file_format='tfm')
if tfm_file is None:
    print 'TFM file %s not found' % (args.font)
    sys.exit(1)

tfm = TfmParser.parse(args.font, tfm_file)
tfm.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
