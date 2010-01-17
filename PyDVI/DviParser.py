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
#  - 17/10/2010 fabrice
#
#####################################################################################################

#####################################################################################################

import os

#####################################################################################################

from EnumFactory import *
from DviMachine import *
from OpcodeParser import *

#####################################################################################################

dvi_opcodes_tuple = []

for i in xrange(128):
    dvi_opcodes_tuple.append('SETC_%03u' % (i))

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

for i in xrange(64):
    dvi_opcodes_tuple.append('FONT_%02u' % (i))

dvi_opcodes_tuple += [
    'FNT1', 'FNT2', 'FNT3', 'FNT4',
    'XXX1', 'XXX2', 'XXX3', 'XXX4',
    'FNT_DEF1', 'FNT_DEF2', 'FNT_DEF3', 'FNT_DEF4',
    'PRE',
    'POST',
    'POST_POST',
    ]

dvi_opcodes = EnumFactory('DviOpcodes', dvi_opcodes_tuple)

###################################################

DVI_EOF_SIGNATURE = 223

dvi_formats = ExplicitEnumFactory('DviFormats',
                                  {'DVI':  2,
                                   'DVIV': 3,
                                   'XDVI': 5,
                                   })

set_char_description = 'typeset a character and move right'

#####################################################################################################

class OpcodeParser_set_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_set_char, self).__init__(opcode,
                                                    'set', set_char_description,
                                                    opcode_class=Opcode_set_char)

    ###############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode]

#####################################################################################################

class OpcodeParser_font(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_font, self).__init__(opcode,
                                                'fnt num', 'set current font to i',
                                                opcode_class = Opcode_font)

    ###############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode - dvi_opcodes.FONT_00]

#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = dvi_opcodes.XXX1

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode,
                                               'xxx', 'extension to DVI primitives',
                                               opcode_class = Opcode_xxx)

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten[self.opcode - self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_parser):

        return [dvi_parser.read(self.read_unsigned_byten(dvi_parser))]

#####################################################################################################

class OpcodeParser_fnt_def(OpcodeParser):

    base_opcode = dvi_opcodes.FNT_DEF1

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_fnt_def, self).__init__(opcode,
                                                   'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten[opcode - self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_parser):

        font_id = self.read_unsigned_byten(dvi_parser)

        font_checksum     = dvi_parser.read_unsigned_byte4()
        font_scale_factor = dvi_parser.read_unsigned_byte4()
        font_design_size  = dvi_parser.read_unsigned_byte4()
        
        font_name = dvi_parser.read(dvi_parser.read_unsigned_byte1() +
                                    dvi_parser.read_unsigned_byte1())

        dvi_parser.dvi_program.register_font(DviFont(font_id,
                                                     font_name,
                                                     font_checksum,
                                                     font_scale_factor,
                                                     font_design_size))

#####################################################################################################

BadDviStream = NameError('Bad DVI stream')

class DviParser(OpcodeStreamParser, StandardStream):

    opcode_definitions = (
        ( [dvi_opcodes.SETC_000,
           dvi_opcodes.SETC_127], OpcodeParser_set_char ),
        ( dvi_opcodes.SET1, 'set', set_char_description, ([1,4]), Opcode_set_char ),
        # ... to SET4
        ( dvi_opcodes.SET_RULE, 'set rule', 'typeset a rule and move right', (4,4), Opcode_set_rule ),
        ( dvi_opcodes.PUT1, 'put', 'typeset a character', ([1,4]), Opcode_put_char ),
        # ... to PUT4
        ( dvi_opcodes.PUT_RULE, 'put rule', 'typeset a rule', (4,4), Opcode_put_rule ),
        ( dvi_opcodes.NOP, 'nop', 'no operation', None, None ),
        ( dvi_opcodes.BOP, 'bop', 'beginning of page', tuple([4]*9 + [-4]), None ),
        ( dvi_opcodes.EOP, 'eop', 'ending of page', None, None ),
        ( dvi_opcodes.PUSH, 'push', 'save the current positions', None, Opcode_push ),
        ( dvi_opcodes.POP, 'pop', 'restore previous positions', None, Opcode_pop ),
        ( dvi_opcodes.RIGHT1, 'right', 'move right', ([-1,-4]), Opcode_right ),
        # ... to RIGHT4
        ( dvi_opcodes.W0, 'w0', 'move right by w', None, Opcode_w0 ),
        ( dvi_opcodes.W1, 'w', 'move right and set w', ([-1,-4]), Opcode_w ),
        # ... to W4
        ( dvi_opcodes.X0, 'x0', 'move right by x', None, Opcode_x0 ),
        ( dvi_opcodes.X1, 'x', 'move right and set x', ([-1,-4]), Opcode_x ),
        # ... to X4
        ( dvi_opcodes.DOWN1, 'down', 'move down', ([-1,-4]), Opcode_down ),
        # ... to DOWN4
        ( dvi_opcodes.Y0, 'y0', 'move down by y', None, Opcode_y0 ),
        ( dvi_opcodes.Y1, 'y', 'move down and set y', ([-1,-4]), Opcode_y ),
        # ... to Y4
        ( dvi_opcodes.Z0, 'z0', 'move down by z', None, Opcode_z0 ),
        ( dvi_opcodes.Z1, 'z', 'move down and set z', ([-1,-4]), Opcode_z ),
        # ... to Z4
        ( [dvi_opcodes.FONT_00,
           dvi_opcodes.FONT_63], OpcodeParser_font ),
        ( dvi_opcodes.FNT1, 'fnt', 'set current font', ([1,4]), Opcode_font ),
        ( [dvi_opcodes.XXX1,
           dvi_opcodes.XXX4], OpcodeParser_xxx ),
        ( [dvi_opcodes.FNT_DEF1,
           dvi_opcodes.FNT_DEF4], OpcodeParser_fnt_def ),
        ( dvi_opcodes.PRE, 'pre', 'preamble', (), None ),
        ( dvi_opcodes.POST, 'post', 'postamble beginning', None, None ),
        ( dvi_opcodes.POST_POST, 'post post', 'postamble ending', None, None ),
        )
   
    ###############################################

    def __init__(self, debug = False):

        self.debug = debug

        super(DviParser, self).__init__(self.opcode_definitions)

    ###############################################

    def reset(self):

        self.dvi_program = DviProgam()

        self.post_pointer = None

        self.page_number = None

        self.bop_pointer_stack = []

    ###############################################

    def open(self, stream):

        self.stream = stream

    ###############################################

    def close(self):

        self.stream = None
       
    ###############################################

    def process_stream(self, stream):

        # Fixme: read pages before postamble

        self.reset()

        self.open(stream)

        self.process_preambule()
        self.process_postambule()
        self.process_pages_backward()

        if self.debug:
            for bop_pointer in self.bop_pointer_stack:
                print 'BOP at', bop_pointer

        self.close()

        return self.dvi_program

    ###############################################

    def process_preambule(self):

        self.seek(0)

        if self.debug:
            print 'Preamble begin at', self.tell()

        if self.read_unsigned_byte1() != dvi_opcodes.PRE:
            raise NameError("DVI stream don't start by PRE")

        dvi_format = self.read_unsigned_byte1()
        if dvi_format not in dvi_formats:
            raise NameError('Unknown DVI Format')

        numerator     = self.read_unsigned_byte4()
        denominator   = self.read_unsigned_byte4()
        magnification = self.read_unsigned_byte4()

        comment = self.read(self.read_unsigned_byte1())

        self.dvi_program.set_preambule_data(comment,
                                            dvi_format,
                                            numerator, denominator, magnification)

        if self.debug:
            print 'Preamble end at', self.tell() -1

    ###############################################

    def process_postambule(self):

        # DVI file end with at least four EOF_SIGNATURE
        
        # Test bytes from -5 

        opcode = dvi_opcodes.NOP

        self.seek(-5, os.SEEK_END)

        while True:

            opcode = self.read_unsigned_byte1()

            if opcode < 0: # found EOF
                raise BadDviStream
            elif opcode != DVI_EOF_SIGNATURE:
                break

            self.seek(-2, os.SEEK_CUR) # seek to previous byte

        dvi_format = opcode

        self.seek(-5, os.SEEK_CUR)
        self.post_pointer = self.read_unsigned_byte4()

        # Move to Postamble
        self.seek(self.post_pointer)

        if self.debug:
            print 'Postamble start at', self.tell()

        if self.read_unsigned_byte1() != dvi_opcodes.POST:
            raise BadDviStream

        self.bop_pointer_stack.append(self.read_signed_byte4())

        numerator     = self.read_unsigned_byte4()
        denominator   = self.read_unsigned_byte4()
        magnification = self.read_unsigned_byte4()

        max_height = self.read_unsigned_byte4()
        max_width  = self.read_unsigned_byte4()
        stack_depth = self.read_unsigned_byte2()
        number_of_pages = self.read_unsigned_byte2()
                                             
        self.number_of_pages = number_of_pages
                                             
        # Read Font definitions

        while True:
            opcode = self.read_unsigned_byte1()
            if opcode >= dvi_opcodes.FNT_DEF1 and opcode <= dvi_opcodes.FNT_DEF4:
                self.opcode_parsers[opcode].read_parameters(self)
            elif opcode != dvi_opcodes.NOP:
                break

        # POST POST

        if opcode != dvi_opcodes.POST_POST:
            raise BadDviStream

        post_pointer = self.read_unsigned_byte4()
        dvi_format = self.read_unsigned_byte1()

        self.dvi_program.set_postambule_data(max_height, max_width,
                                             stack_depth,
                                             number_of_pages)

    ###############################################

    def process_pages_backward(self):

        '''
        Process pages in backward order
        '''

        self.page_number = self.number_of_pages

        bop_pointer = self.bop_pointer_stack[0]

        while bop_pointer >= 0:

            self.page_number -= 1

            self.seek(bop_pointer)

            if self.debug:
                print 'BOP at', self.tell()

            opcode = self.read_unsigned_byte1()

            if opcode != dvi_opcodes.BOP:
                raise BadDviStream

            counts = [self.read_unsigned_byte4() for i in xrange(10)]

            bop_pointer = self.read_signed_byte4()

            self.bop_pointer_stack.append(bop_pointer)

            page = self.process_page()

    ###############################################

    def process_page(self):

        opcode_program = self.dvi_program.get_page(self.page_number)
        
        previous_opcode_obj = None

        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == dvi_opcodes.EOP:
                break

            else:
                opcode_parser = self.opcode_parsers[opcode]

                parameters = opcode_parser.read_parameters(self)

                if self.debug:
                    print 'Opcode', opcode, opcode_parser.name, parameters

                # If the current and the previous opcode correspond to set char
                # then the new char is concatenated

                is_set_char = opcode <= dvi_opcodes.SET4

                if is_set_char and previous_opcode_obj is not None:
                    previous_opcode_obj.append(parameters[0])
                else:
                    opcode_obj = opcode_parser.to_opcode(parameters) 

                    if opcode_obj is not None:
                        opcode_program.append(opcode_obj)

                    if is_set_char:
                        previous_opcode_obj = opcode_obj
                    else:
                        previous_opcode_obj = None

#####################################################################################################
#
#                                               Test
#
#####################################################################################################
        
if __name__ == '__main__':

    from optparse import OptionParser

    usage = 'usage: %prog [options]'

    parser = OptionParser(usage)

    opt, args = parser.parse_args()

    dvi_file = args[0]

    ###############################################

    dvi_parser = DviParser(debug = True)

    dvi_machine = DviMachine()


    dvi_stream = open(dvi_file)

    dvi_program = dvi_parser.process_stream(dvi_stream)

    dvi_stream.close()


    dvi_program.print_summary()

    # print 'Run last page:'
    # if len(dvi_program.pages) > 0:
    #     dvi_machine.run(dvi_program, -1)

#####################################################################################################
#
# End
#
#####################################################################################################
