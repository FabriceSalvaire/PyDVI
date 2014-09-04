####################################################################################################
#
# PyDvi - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
# - 17/12/2011 fabrice
#
####################################################################################################

####################################################################################################

import argparse
import logging

####################################################################################################

from PyDvi.Dvi.DviMachine import DviMachine
from PyDvi.Dvi.DviParser import DviParser 
from PyDvi.Font.FontManager import FontManager
from PyDvi.Tools.Stream import FileStream

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

parser = argparse.ArgumentParser(description='Test DViMachine.')
parser.add_argument('dvi', metavar='DviFile',
                    help='DVI file')
args = parser.parse_args()

####################################################################################################

font_manager = FontManager(font_map='pdftex', use_pk=True)
dvi_parser = DviParser()
dvi_machine = DviMachine(font_manager)

dvi_stream = FileStream(args.dvi)
dvi_program = dvi_parser.process_stream(dvi_stream)
del dvi_stream

line = '='*80

print
dvi_program.print_summary()

dvi_machine.load_dvi_program(dvi_program)
print line
dvi_program[0].print_program()
print line
dvi_machine.simplify_dvi_program()
print line
dvi_program[0].print_program()
print line

print 'Compute bounding box of the first page:'
dvi_machine.compute_page_bounding_box(0)

print line
print 'Run the first page:'
dvi_machine.run_page(0)

#print 'Compute bounding box of the last page:'
# if len(dvi_program.pages) > 0:
#     dvi_machine.compute_page_bounding_box(-1)
# 
# print '\n', '-'*80, '\n'
# 
# print 'Run last page:'
# if len(dvi_program.pages) > 0:
#     dvi_machine.run_page(-1)

####################################################################################################
#
# End
#
####################################################################################################
