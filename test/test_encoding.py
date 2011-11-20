#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
#                                              Audit
#
# - 13/11/2011 Fabrice
#   x
#
#####################################################################################################

#####################################################################################################

import sys

from optparse import OptionParser

#####################################################################################################

from PyDVI.Encoding import Encoding
from PyDVI.Kpathsea import kpsewhich

#####################################################################################################

usage = 'usage: %prog encoding'

parser = OptionParser(usage)

opt, args = parser.parse_args()

if len(args) != 1:
    parser.error("Give a TeX encoding, e.g. cork")

encoding = args[0]

#####################################################################################################

encoding_file = kpsewhich(encoding, file_format='enc files')

if encoding_file is None:
    print 'Encoding %s not found' % (encoding)
    sys.exit(1)

print 'Read %s encoding file' % (encoding_file)

encoding = Encoding(encoding_file)
encoding.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
