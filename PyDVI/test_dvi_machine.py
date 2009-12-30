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
#  - 19/12/2009 fabrice
#
#####################################################################################################

#####################################################################################################

import sys

from optparse import OptionParser

#####################################################################################################

from DviParser import DviParser 
from DviMachine import *
from FontManager import *

#####################################################################################################

usage = 'usage: %prog [options]'

parser = OptionParser(usage)

opt, args = parser.parse_args()

dvi_file = args[0]

#####################################################################################################

dvi_parser = DviParser(debug = False)

font_manager = FontManager(font_map = 'pdftex', use_pk = False)

dvi_machine = DviMachine(font_manager)

###################################################

dvi_stream = open(dvi_file)

dvi_program = dvi_parser.process_stream(dvi_stream)

dvi_stream.close()

###################################################

dvi_program.print_summary()

dvi_machine.load_dvi_program(dvi_program)

dvi_machine.simplify_dvi_program()

dvi_program[0].print_program()

sys.exit(0)

print 'Compute bounding box of the last page:'
if len(dvi_program.pages) > 0:
    dvi_machine.compute_page_bounding_box(-1)

print '\n', '-'*80, '\n'

print 'Run last page:'
if len(dvi_program.pages) > 0:
    dvi_machine.run_page(-1)

#####################################################################################################
#
# End
#
#####################################################################################################
