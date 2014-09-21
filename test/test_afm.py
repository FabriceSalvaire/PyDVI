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
import sys

####################################################################################################

import PyDvi.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PyDvi.Font.AfmParser import AfmParser
from PyDvi.Kpathsea import kpsewhich

####################################################################################################

parser = argparse.ArgumentParser(description='Test AFM.')
# parser.add_argument('font', metavar='Font',
#                     help='Font name, e.g. uhvr8a')
parser.add_argument('afm_file', metavar='FILE.afm',
                    help='afm file')
args = parser.parse_args()

####################################################################################################

# afm_file = kpsewhich(args.font, file_format='afm')
# if afm_file is None:
#     print 'AFM file %s not found' % (args.font)
#     sys.exit(1)

afm_file = args.afm_file
afm = AfmParser.parse(afm_file)

####################################################################################################
#
# End
#
####################################################################################################
