#####################################################################################################

import string

#####################################################################################################

from DviMachine import *
from DviDefinition import *
from OpcodeParser import *

#####################################################################################################

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

set_char_description = 'typeset a character and move right'

#####################################################################################################

class OpcodeParser_set_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_set_char, self).__init__(opcode, 'set', set_char_description,
                                                    opcode_class = Opcode_set_char)

    ###############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode]

#####################################################################################################

class OpcodeParser_font(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_font, self).__init__(opcode, 'fnt num', 'set current font to i',
                                                opcode_class = Opcode_font)

    ###############################################

    def read_parameters(self, dvi_parser):

        return [self.opcode - FONT_00_OPCODE]

#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = XXX1_OPCODE

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'extension to DVI primitives',
                                               opcode_class = Opcode_xxx)

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten_pointer[self.opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_parser):

        return [dvi_parser.read_stream(self.read_unsigned_byten(dvi_parser))]

#####################################################################################################

class OpcodeParser_fnt_def(OpcodeParser):

    base_opcode = 243

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_fnt_def, self).__init__(opcode, 'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_parser):

        font_id = self.read_unsigned_byten(dvi_parser)

        font_checksum     = dvi_parser.read_unsigned_byte4()
        font_scale_factor = dvi_parser.read_unsigned_byte4()
        font_design_size  = dvi_parser.read_unsigned_byte4()
        
        font_name = dvi_parser.read_stream(dvi_parser.read_unsigned_byte1() +
                                           dvi_parser.read_unsigned_byte1())

        dvi_parser.dvi_program.register_font(DviFont(font_id,
                                                     font_name,
                                                     font_checksum,
                                                     font_scale_factor,
                                                     font_design_size))

#####################################################################################################

class DviParser(OpcodeStreamParser):

    opcode_definitions = (
        ( [SETC_000_OPCODE, SETC_127_OPCODE], OpcodeParser_set_char ),
        ( SET1_OPCODE, 'set', set_char_description, ([1,4]), Opcode_set_char ),
        ( SET_RULE_OPCODE, 'set rule', 'typeset a rule and move right', (4,4), Opcode_set_rule ),
        ( PUT1_OPCODE, 'put', 'typeset a character', ([1,4]), Opcode_put_char ),
        ( PUT_RULE_OPCODE, 'put rule', 'typeset a rule', (4,4), Opcode_put_rule ),
        ( NOP_OPCODE, 'nop', 'no operation', None, None ),
        ( BOP_OPCODE, 'bop', 'beginning of page', tuple([4]*9 + [-4]), None ),
        ( EOP_OPCODE, 'eop', 'ending of page', None, None ),
        ( PUSH_OPCODE, 'push', 'save the current positions', None, Opcode_push ),
        ( POP_OPCODE, 'pop', 'restore previous positions', None, Opcode_pop ),
        ( RIGHT1_OPCODE, 'right', 'move right', ([-1,-4]), Opcode_right ),
        ( W0_OPCODE, 'w0', 'move right by w', None, Opcode_w0 ),
        ( W1_OPCODE, 'w', 'move right and set w', ([-1,-4]), Opcode_w ),
        ( X0_OPCODE, 'x0', 'move right by x', None, Opcode_x0 ),
        ( X1_OPCODE, 'x', 'move right and set x', ([-1,-4]), Opcode_x ),
        ( DOWN1_OPCODE, 'down', 'move down', ([-1,-4]), Opcode_down ),
        ( Y0_OPCODE, 'y0', 'move down by y', None, Opcode_y0 ),
        ( Y1_OPCODE, 'y', 'move down and set y', ([-1,-4]), Opcode_y ),
        ( Z0_OPCODE, 'z0', 'move down by z', None, Opcode_z0 ),
        ( Z1_OPCODE, 'z', 'move down and set z', ([-1,-4]), Opcode_z ),
        ( [FONT_00_OPCODE, FONT_63_OPCODE], OpcodeParser_font ),
        ( FNT1_OPCODE, 'fnt', 'set current font', ([1,4]), Opcode_font ),
        ( [XXX1_OPCODE, XXX4_OPCODE], OpcodeParser_xxx ),
        ( [FNT_DEF1_OPCODE, FNT_DEF4_OPCODE], OpcodeParser_fnt_def ),
        ( PRE_OPCODE, 'pre', 'preamble', (), None ),
        ( POST_OPCODE, 'post', 'postamble beginning', None, None ),
        ( POST_POST_OPCODE, 'post post', 'postamble ending', None, None ),
        )
   
    ###############################################

    def __init__(self):

        super(DviParser, self).__init__(self.opcode_definitions)

    ###############################################

    def reset(self):

        self.dvi_program = DviProgam()

        self.bop_pointer_stack = []

        self.page_number = None
        
    ###############################################

    def process_stream(self, stream):

        # Fixme: read pages before postamble

        self.set_stream(stream)

        self.reset()

        self.process_preambule()
        self.process_postambule()
        self.process_pages()

        for bop_pointer in self.bop_pointer_stack:
            print 'BOP pointer pos = ', bop_pointer

        self.set_stream(None)

        return self.dvi_program

    ###############################################

    def process_preambule(self):

        self.stream.seek(0)

        print 'Preamble Begin pos =', self.tell()

        if self.read_unsigned_byte1() != PRE_OPCODE:
            raise NameError('Bad DVI stream')

        dvi_format = self.read_unsigned_byte1()
        if dvi_format not in (DVI_FORMAT, DVIV_FORMAT, XDVI_FORMAT):
            raise NameError('Bad DVI Format')

        numerator     = self.read_unsigned_byte4()
        denominator   = self.read_unsigned_byte4()
        magnification = self.read_unsigned_byte4()

        comment = self.read_stream(self.read_unsigned_byte1())

        self.dvi_program.set_preambule_data(comment,
                                            dvi_format,
                                            numerator, denominator, magnification)

        print 'Preamble End pos =', self.tell() -1

    ###############################################

    def process_postambule(self):

        # DVI file end with at least four EOF_SIGNATURE
        
        # Test -5 byte

        opcode = NOP_OPCODE

        self.stream.seek(-5, SEEK_RELATIVE_TO_END)

        while True:

            opcode = self.read_unsigned_byte1()

            if opcode < 0: # found EOF
                raise NameError('Bad DVI stream')
            elif opcode != EOF_SIGNATURE:
                break

            self.stream.seek(-2, SEEK_RELATIVE_TO_CURRENT)

        dvi_format = opcode

        self.stream.seek(-5, SEEK_RELATIVE_TO_CURRENT)
        self.post_pointer = self.read_unsigned_byte4()

        # Move to post
        self.stream.seek(self.post_pointer)

        print 'Postamble Start pos', self.tell()

        if self.read_unsigned_byte1() != POST_OPCODE:
            raise NameError('Bad DVI stream')            

        self.bop_pointer_stack.append(self.read_signed_byte4())

        numerator     = self.read_unsigned_byte4()
        denominator   = self.read_unsigned_byte4()
        magnification = self.read_unsigned_byte4()

        max_height = self.read_unsigned_byte4()
        max_width  = self.read_unsigned_byte4()
        stack_depth = self.read_unsigned_byte2()
        number_of_pages = self.read_unsigned_byte2()
                                             
        self.number_of_pages = number_of_pages
                                             
        # Read Font definition

        while True:
            opcode = self.read_unsigned_byte1()
            if opcode >= FNT_DEF1_OPCODE and opcode <= FNT_DEF4_OPCODE:
                self.opcode_parsers[opcode].read_parameters(self)
            elif opcode != NOP_OPCODE:
                break

        # POST POST

        if opcode != POST_POST_OPCODE:
            raise NameError('Bad DVI stream')

        post_pointer = self.read_unsigned_byte4()
        dvi_format = self.read_unsigned_byte1()

        self.dvi_program.set_postambule_data(max_height, max_width,
                                             stack_depth,
                                             number_of_pages)

    ###############################################

    def process_pages(self):

        self.page_number = self.number_of_pages

        bop_pointer = self.bop_pointer_stack[0]

        while bop_pointer >= 0:

            self.page_number -= 1

            self.stream.seek(bop_pointer)

            print 'BOP pos', self.tell()

            opcode = self.read_unsigned_byte1()

            if opcode != BOP_OPCODE:
                raise NameError('Bad DVI stream')

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

            if opcode == EOP_OPCODE:
                break
            else:
                opcode_parser = self.opcode_parsers[opcode]

                parameters = opcode_parser.read_parameters(self)

                # print opcode, opcode_parser.name, parameters

                is_set_char = opcode <= SET4_OPCODE

                if is_set_char is True and previous_opcode_obj is not None:
                    previous_opcode_obj.append(parameters)
                else:
                    opcode_obj = opcode_parser.to_opcode(parameters) 

                    if opcode_obj is not None:
                        opcode_program.append(opcode_obj)

                    if is_set_char is True:
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

    dvi_parser = DviParser()

    dvi_machine = DviMachine()


    dvi_stream = open(dvi_file)

    dvi_program = dvi_parser.process_stream(dvi_stream)

    dvi_stream.close()


    dvi_program.print_summary()

    print 'Run last page:'
    if len(dvi_program.pages) > 0:
        dvi_machine.run(dvi_program, -1)

#####################################################################################################
#
# End
#
#####################################################################################################
