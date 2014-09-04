####################################################################################################
#
# PyDvi - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
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
