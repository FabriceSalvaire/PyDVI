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

""" This module implements a DVI Stream Parser.
"""

####################################################################################################

import logging
import os

####################################################################################################

from .DviMachine import *
from ..OpcodeParser import OpcodeParserSet, OpcodeParser
from ..Tools.EnumFactory import EnumFactory, ExplicitEnumFactory
from ..Tools.Stream import AbstractStream

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

dvi_opcodes_tuple = ['SETC_%03u' % (i) for i in xrange(128)]

dvi_opcodes_tuple += [
    'SET1', 'SET2', 'SET3', 'SET4',
    'SET_RULE',
    'PUT1', 'PUT2', 'PUT3', 'PUT4',
    'PUT_RULE',
    'NOP',
    'BOP',
    'EOP',
    'PUSH',
    'POP',
    'RIGHT1', 'RIGHT2', 'RIGHT3', 'RIGHT4',
    'W0', 'W1', 'W2', 'W3', 'W4',
    'X0', 'X1', 'X2', 'X3', 'X4',
    'DOWN1', 'DOWN2', 'DOWN3', 'DOWN4',
    'Y0', 'Y1', 'Y2', 'Y3', 'Y4',
    'Z0', 'Z1', 'Z2', 'Z3', 'Z4',
    ]

dvi_opcodes_tuple += ['FONT_%02u' % (i) for i in xrange(64)]

dvi_opcodes_tuple += [
    'FNT1', 'FNT2', 'FNT3', 'FNT4',
    'XXX1', 'XXX2', 'XXX3', 'XXX4',
    'FNT_DEF1', 'FNT_DEF2', 'FNT_DEF3', 'FNT_DEF4',
    'PRE',
    'POST',
    'POST_POST',
    ]

dvi_opcodes = EnumFactory('DviOpcodes', dvi_opcodes_tuple)

####################################################################################################

DVI_EOF_SIGNATURE = 223

dvi_formats = ExplicitEnumFactory('DviFormats',
                                  {'DVI':  2,
                                   'DVIV': 3,
                                   'XDVI': 5,
                                   })

set_char_description = 'typeset a character and move right'

####################################################################################################

class OpcodeParser_set_char(OpcodeParser):

    """ This class parse the ``set_char`` opcode. """

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_set_char, self).__init__(opcode,
                                                    'set', set_char_description,
                                                    opcode_class=Opcode_set_char)

    ##############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode]

####################################################################################################

class OpcodeParser_font(OpcodeParser):

    """ This class parse the ``font`` opcode. """

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_font, self).__init__(opcode,
                                                'fnt num', 'set current font to i',
                                                opcode_class=Opcode_font)

    ##############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode - dvi_opcodes.FONT_00]

####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    """ This class parse the ``xxx`` opcode. """

    base_opcode = dvi_opcodes.XXX1

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode,
                                               'xxx', 'extension to DVI primitives',
                                               opcode_class=Opcode_xxx)

        self.read_unsigned_byten = AbstractStream.read_unsigned_byten[self.opcode - self.base_opcode]

    ##############################################

    def read_parameters(self, dvi_parser):

        stream = dvi_parser.stream

        return [str(stream.read(self.read_unsigned_byten(stream)))]

####################################################################################################

class OpcodeParser_fnt_def(OpcodeParser):

    """ This class parse the ``fnt_def`` opcode. """

    base_opcode = dvi_opcodes.FNT_DEF1

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_fnt_def, self).__init__(opcode,
                                                   'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = AbstractStream.read_unsigned_byten[opcode - self.base_opcode]

    ##############################################

    def read_parameters(self, dvi_parser):

        stream = dvi_parser.stream

        font_id = self.read_unsigned_byten(stream)
        font_checksum = stream.read_unsigned_byte4()
        font_scale_factor = stream.read_unsigned_byte4()
        font_design_size = stream.read_unsigned_byte4()
        font_name = str(stream.read(stream.read_unsigned_byte1() + stream.read_unsigned_byte1()))

        font = DviFont(font_id, font_name, font_checksum, font_scale_factor, font_design_size)
        dvi_parser.dvi_program.register_font(font)

####################################################################################################

BadDviStream = NameError('Bad DVI stream')

####################################################################################################

class DviParser(object):

    """ This class implements a DVI Stream Parser.
    """

    _logger = _module_logger.getChild('DviParser')

    opcode_definitions = (
        ( [dvi_opcodes.SETC_000,
           dvi_opcodes.SETC_127], OpcodeParser_set_char ),
        ( dvi_opcodes.SET1, 'set', set_char_description, [1,4], Opcode_set_char ),
        # ... to SET4
        ( dvi_opcodes.SET_RULE, 'set rule', 'typeset a rule and move right', (4,4), Opcode_set_rule ),
        ( dvi_opcodes.PUT1, 'put', 'typeset a character', [1,4], Opcode_put_char ),
        # ... to PUT4
        ( dvi_opcodes.PUT_RULE, 'put rule', 'typeset a rule', (4,4), Opcode_put_rule ),
        ( dvi_opcodes.NOP, 'nop', 'no operation', None, None ),
        ( dvi_opcodes.BOP, 'bop', 'beginning of page', tuple([4]*9 + [-4]), None ),
        ( dvi_opcodes.EOP, 'eop', 'ending of page', None, None ),
        ( dvi_opcodes.PUSH, 'push', 'save the current positions', None, Opcode_push ),
        ( dvi_opcodes.POP, 'pop', 'restore previous positions', None, Opcode_pop ),
        ( dvi_opcodes.RIGHT1, 'right', 'move right', [-1,-4], Opcode_right ),
        # ... to RIGHT4
        ( dvi_opcodes.W0, 'w0', 'move right by w', None, Opcode_w0 ),
        ( dvi_opcodes.W1, 'w', 'move right and set w', [-1,-4], Opcode_w ),
        # ... to W4
        ( dvi_opcodes.X0, 'x0', 'move right by x', None, Opcode_x0 ),
        ( dvi_opcodes.X1, 'x', 'move right and set x', [-1,-4], Opcode_x ),
        # ... to X4
        ( dvi_opcodes.DOWN1, 'down', 'move down', [-1,-4], Opcode_down ),
        # ... to DOWN4
        ( dvi_opcodes.Y0, 'y0', 'move down by y', None, Opcode_y0 ),
        ( dvi_opcodes.Y1, 'y', 'move down and set y', [-1,-4], Opcode_y ),
        # ... to Y4
        ( dvi_opcodes.Z0, 'z0', 'move down by z', None, Opcode_z0 ),
        ( dvi_opcodes.Z1, 'z', 'move down and set z', [-1,-4], Opcode_z ),
        # ... to Z4
        ( [dvi_opcodes.FONT_00,
           dvi_opcodes.FONT_63], OpcodeParser_font ),
        ( dvi_opcodes.FNT1, 'fnt', 'set current font', [1,4], Opcode_font ),
        ( [dvi_opcodes.XXX1,
           dvi_opcodes.XXX4], OpcodeParser_xxx ),
        ( [dvi_opcodes.FNT_DEF1,
           dvi_opcodes.FNT_DEF4], OpcodeParser_fnt_def ),
        ( dvi_opcodes.PRE, 'pre', 'preamble', (), None ),
        ( dvi_opcodes.POST, 'post', 'postamble beginning', None, None ),
        ( dvi_opcodes.POST_POST, 'post post', 'postamble ending', None, None ),
        )

    opcode_parser_set = OpcodeParserSet(opcode_definitions)
   
    ##############################################

    def _reset(self):

        """ Reset the DVI parser. """

        self.dvi_program = DviProgam()
        self.post_pointer = None
        self.page_number = None
        self.bop_pointer_stack = [] # can be used for lazy loading, reverse if backward
     
    ##############################################

    def process_stream(self, stream):

        """ Process a DVI stream and return a :class:`DviProgam` instance. """

        # Fixme: read pages before postamble (note: why ?)
        # Fixme: it would be better to read page on demand for long documents.

        self._reset()
        self.stream = stream
        self._process_preambule()
        self._process_postambule()
        self._process_pages_backward() # Fixme: retrieve bop pointers but don't read the page
        self.stream = None

        return self.dvi_program

    ##############################################

    def _process_preambule(self):

        """ Process the preamble where we get the magnification. """

        self._logger.debug('Process the preamble')

        stream = self.stream

        stream.seek(0)
        if stream.read_unsigned_byte1() != dvi_opcodes.PRE:
            raise NameError("DVI stream don't start by PRE")

        dvi_format = stream.read_unsigned_byte1()
        if dvi_format not in dvi_formats:
            raise NameError('Unknown DVI Format')

        numerator = stream.read_unsigned_byte4()
        denominator = stream.read_unsigned_byte4()
        magnification = stream.read_unsigned_byte4()
        comment = stream.read(stream.read_unsigned_byte1())

        self.dvi_program.set_preambule_data(comment,
                                            dvi_format,
                                            numerator, denominator, magnification)

        self._logger.debug('Preamble end at {}'.format(stream.tell() -1))

    ##############################################

    def _process_postambule(self):

        """ Process the postamble where we get the number of pages and the fonts. """

        # DVI postamble format:
        #   postamble: post opcode
        #   <font definitions>
        #   post post opcode
        #     post pointer
        #     dvi format
        #   EOF_SIGNATURE [at least 4 times]

        self._logger.debug('Process the postamble')

        stream = self.stream

        # DVI file end with at least four EOF_SIGNATURE
        # Read stream[-5] and move backward until opcode != EOF_SIGNATURE
        stream.seek(-5, os.SEEK_END)
        while True:
            opcode = stream.read_unsigned_byte1()
            if opcode != DVI_EOF_SIGNATURE:
                break
            else:
                # seek to previous byte
                stream.seek(-2, os.SEEK_CUR)
        # We read the dvi format
        dvi_format = opcode

        # Move backward and read post pointer
        stream.seek(-5, os.SEEK_CUR)
        self.post_pointer = stream.read_unsigned_byte4()

        # Move to Postamble
        stream.seek(self.post_pointer)
        self._logger.debug('Postamble start at {}'.format(stream.tell()))

        if stream.read_unsigned_byte1() != dvi_opcodes.POST:
            raise BadDviStream

        # Push pointer to the last page
        self.bop_pointer_stack.append(stream.read_signed_byte4())

        numerator = stream.read_unsigned_byte4()
        denominator = stream.read_unsigned_byte4()
        magnification = stream.read_unsigned_byte4()
        max_height = stream.read_unsigned_byte4()
        max_width  = stream.read_unsigned_byte4()
        stack_depth = stream.read_unsigned_byte2()
        number_of_pages = stream.read_unsigned_byte2()
                                             
        # Read Font definitions
        while True:
            opcode = stream.read_unsigned_byte1()
            if dvi_opcodes.FNT_DEF1 <= opcode <= dvi_opcodes.FNT_DEF4:
                self.opcode_parser_set[opcode].read_parameters(self)
            elif opcode != dvi_opcodes.NOP:
                break
            # Fixme: else

        # We must reach POST POST
        if opcode != dvi_opcodes.POST_POST:
            raise BadDviStream

        # post_pointer = stream.read_unsigned_byte4()
        # dvi_format = stream.read_unsigned_byte1()

        self.number_of_pages = number_of_pages
        self.dvi_program.set_postambule_data(max_height, max_width, stack_depth, number_of_pages)

        self._logger.debug('Number of pages: {}'.format(number_of_pages))
        self._logger.debug('Stack depth: {}'.format(stack_depth))

    ##############################################

    def _process_pages_backward(self):

        """ Process the pages in backward order.
        """

        self._logger.debug('Process the pages in backward order.')

        stream = self.stream
        self.page_number = self.number_of_pages

        # Get pointer to the last page
        bop_pointer = self.bop_pointer_stack[0]
        # Move backward from page to page and process the pages
        while bop_pointer >= 0:
            stream.seek(bop_pointer)
            self.page_number -= 1
            self._logger.debug('BOP at {}, page # {}'.format(stream.tell(), self.page_number))

            opcode = stream.read_unsigned_byte1()
            if opcode != dvi_opcodes.BOP:
                raise BadDviStream

            counts = [stream.read_unsigned_byte4() for i in xrange(10)]

            bop_pointer = stream.read_signed_byte4()
            self.bop_pointer_stack.append(bop_pointer)

            # Fixme: page?
            page = self.process_page()

    ##############################################

    def process_page_forward(self):

        # Fixme: test this code

        stream = self.stream

        if self.page_number is None:
            self.page_number = 0
        else:
            self.page_number += 1
        self.dvi_program.append_page(self.page_number)
        self._logger.debug('BOP at {}, page # {}'.format(stream.tell(), self.page_number))

        opcode = stream.read_unsigned_byte1()
        if opcode != dvi_opcodes.BOP:
            raise BadDviStream

        counts = [stream.read_unsigned_byte4() for i in xrange(10)]

        bop_pointer = stream.read_signed_byte4()
        #? forward # self.bop_pointer_stack.append(bop_pointer)

        # Fixme: page?
        page = self.process_page()

    ##############################################

    def process_page(self):

        stream = self.stream
        opcode_program = self.dvi_program.get_page(self.page_number)

        # Define some counters to track fonts, characters and rules
        # These counters are intended to allocate memory at the beginning of a page rendering.
        font_id = None
        char_counter = {}
        rule_counter = 0

        # opcode tracker to merge char opcode
        previous_opcode_obj = None
        previous_opcode_was_set = None

        # Fixme: tracking versus program simplification
        #   could merge same opcode using a test and a merge method
        #   char pop push positionning

        while True:
            opcode = stream.read_unsigned_byte1()
            if opcode == dvi_opcodes.EOP:
                break
            else:
                opcode_parser = self.opcode_parser_set[opcode]
                parameters = opcode_parser.read_parameters(self)
                # self._logger.debug('Opcode {} {} {}'.format(opcode, opcode_parser.name, parameters))

                # count characters by font
                is_font = dvi_opcodes.FONT_00 <= opcode <= dvi_opcodes.FNT4
                is_set_char = opcode <= dvi_opcodes.SET4 # SET1 == 0
                is_put_char = dvi_opcodes.PUT1 <= opcode <= dvi_opcodes.PUT4
                is_char = is_set_char or is_put_char
                if is_char:
                    if font_id in char_counter:
                        char_counter[font_id] += 1
                    else:
                        char_counter[font_id] = 1

                # count rules
                is_rule = opcode == dvi_opcodes.SET_RULE or opcode == dvi_opcodes.PUT_RULE
                if is_rule:
                    rule_counter += 1

                # If the current and the previous opcode correspond to set/put char then the new
                # char is concatenated.
                if (is_char
                    and previous_opcode_obj is not None
                    and previous_opcode_was_set == is_set_char):
                    previous_opcode_obj.append(parameters[0])
                else:
                    opcode_obj = opcode_parser.to_opcode(parameters) 
                    if opcode_obj is not None:
                        opcode_program.append(opcode_obj)
                    if is_font:
                        font_id = opcode_obj.font_id
                    if is_char:
                        previous_opcode_obj = opcode_obj
                        previous_opcode_was_set = is_set_char
                    else:
                        previous_opcode_obj = None
                        previous_opcode_was_set = None
        # end of while loop

        opcode_program.number_of_chars = char_counter
        opcode_program.number_of_rules = rule_counter

####################################################################################################
#
# End
#
####################################################################################################
