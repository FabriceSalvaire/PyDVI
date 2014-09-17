####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

import argparse
import logging
import sys

####################################################################################################

from PyDvi.Font.VfFont import VfFont
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

vf_font = VfFont(font_manager=None, font_id=0, name=args.font)
vf_font.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
