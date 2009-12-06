#####################################################################################################

import string

#####################################################################################################

from DviMachine import *
from DviDefinition import *

#####################################################################################################

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

set_char_description = 'typeset a character and move right'

opcode_parsers = [None]*255

#####################################################################################################

class DviParser(object):
    
    ###############################################

    def __init__(self):

        pass

    ###############################################

    def reset(self):

        self.dvi_format    = DVI_FORMAT
        self.numerator     = 25400000
        self.denominator   = 7227*2**16
        self.magnification = 1000
        self.comment       = ''

        self.fonts = {}

        self.bop_pointer_stack = []

        self.page_opcode_programs = []

        self.page_number = None
        
    ###############################################

    def process_stream(self, stream):

        self.stream = stream

        self.reset()

        self.process_preambule()
        self.process_postambule()
        self.process_pages()

    ###############################################

    def read_stream(self, n):

        '''Read the DVI input stream

        n > 0, exception ...
        '''

        return self.stream.read(n)

    def read_big_endian_number(self, n, signed = False):

        '''Read a number coded in big endian format from the DVI input stream

        can unroll
        '''

        bytes = map(ord, self.read_stream(n))

        number = bytes[0]

        if signed is True and number >= 128:
            number -= 256

        for i in xrange(1,n):
            number *= 256
            number += bytes[i]

        return number
            
    def read_unsigned_byte1(self):
        return self.read_big_endian_number(1, signed = False)

    def read_signed_byte1(self):
        return self.read_big_endian_number(1, signed = True)

    def read_unsigned_byte2(self):
        return self.read_big_endian_number(2, signed = False)

    def read_signed_byte2(self):
        return self.read_big_endian_number(2, signed = True)

    def read_unsigned_byte3(self):
        return self.read_big_endian_number(3, signed = False)

    def read_signed_byte3(self):
        return self.read_big_endian_number(3, signed = True)

    def read_signed_byte4(self):
        return self.read_big_endian_number(4, signed = True)

    ###############################################

    def process_preambule(self):

        self.stream.seek(0)

        if self.read_unsigned_byte1() != PRE_OPCODE:
            raise NameError('Bad DVI stream')

        self.dvi_id = self.read_unsigned_byte1()
        if self.dvi_id not in (DVI_FORMAT, DVIV_FORMAT, XDVI_FORMAT):
            raise NameError('Bad DVI Format')

        self.numerator     = self.read_signed_byte4()
        self.denominator   = self.read_signed_byte4()
        self.magnification = self.read_signed_byte4()

        self.comment = self.read_stream(self.read_unsigned_byte1())

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
        self.post_pointer = self.read_signed_byte4()

        # Move to post
        self.stream.seek(self.post_pointer)

        if self.read_unsigned_byte1() != POST_OPCODE:
            raise NameError('Bad DVI stream')            

        self.bop_pointer_stack.append(self.read_signed_byte4())

        numerator     = self.read_signed_byte4()
        denominator   = self.read_signed_byte4()
        magnification = self.read_signed_byte4()

        self.max_height = self.read_signed_byte4()
        self.max_width  = self.read_signed_byte4()
        self.stack_depth = self.read_unsigned_byte2()
        self.number_of_pages = self.read_unsigned_byte2()

        # Read Font definition

        while True:
            opcode = self.read_unsigned_byte1()
            if opcode >= FNT_DEF1_OPCODE and opcode <= FNT_DEF4_OPCODE:
                opcode_parsers[opcode].read_parameters(self)
            elif opcode != NOP_OPCODE:
                break

        # POST POST

        if opcode != POST_POST_OPCODE:
            raise NameError('Bad DVI stream')

        post_pointer = self.read_signed_byte4()
        dvi_format = self.read_unsigned_byte1()

    ###############################################

    def define_font(self, font_id, font_name, font_checksum, font_scale_factor, font_design_size):

        self.fonts[font_id] = {'name':font_name,
                               'checksum':font_checksum,
                               'scale_factor':font_scale_factor,
                               'design_size':font_design_size}

    ###############################################

    def process_pages(self):

        for i in xrange(self.number_of_pages):
            self.page_opcode_programs.append(OpcodeProgram())

        self.page_number = self.number_of_pages

        bop_pointer = self.bop_pointer_stack[0]

        while bop_pointer >= 0:

            self.page_number -= 1

            self.stream.seek(bop_pointer)

            opcode = self.read_unsigned_byte1()

            if opcode != BOP_OPCODE:
                raise NameError('Bad DVI stream')

            counts = [self.read_signed_byte4() for i in xrange(10)]

            bop_pointer = self.read_signed_byte4()

            self.bop_pointer_stack.append(bop_pointer)

            page = self.process_page()

    ###############################################

    def process_page(self):

        opcode_program = self.page_opcode_programs[self.page_number]
        
        previous_opcode_obj = None

        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == EOP_OPCODE:
                break
            else:
                opcode_parser = opcode_parsers[opcode]
                
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

    ###############################################

    def print_summary(self):

        print '''DVI

Preambule
  - DVI format    %u
  - numerator     %u
  - denominator   %u
  - magnification %u
  - comment       '%s'

Postamble
  - max height      %u
  - max width       %u
  - stack depth     %u
  - number of pages %u

Fonts''' % (self.dvi_format, self.numerator, self.denominator, self.magnification, self.comment,
            self.max_height, self.max_width, self.stack_depth, self.number_of_pages)

        for font_id in self.fonts.keys():
            print '  id = %4u' % (font_id), self.fonts[font_id]

        # for i in xrange(self.number_of_pages):
        #     print '\nPage', i
        #     self.page_opcode_programs[i].print_program()

    ###############################################

    read_unsigned_byten_pointer = (read_unsigned_byte1, 
                                   read_unsigned_byte2,
                                   read_unsigned_byte3,
                                   read_signed_byte4)

#####################################################################################################

class OpcodeParser(object):

    ###############################################

    def __init__(self, opcode, name, description, parameters = (), opcode_class = None):

        self.opcode = opcode
        self.name = name
        self.description = description
        self.opcode_class = opcode_class

        self.parameter_readers = []

        if parameters is not None and len(parameters) > 0:
            self.__init_parameter_readers__(parameters)

    ###############################################

    def __str__(self):

        return 'opcode %3u %s %s' % (self.opcode, self.name, self.description)

    ###############################################

    def __init_parameter_readers__(self, parameters):

        for parameter in parameters:
            if   parameter == 1:
                parameter_reader = DviParser.read_unsigned_byte1
            elif parameter == 2:
                parameter_reader = DviParser.read_unsigned_byte2
            elif parameter == 3:
                parameter_reader = DviParser.read_unsigned_byte3
            elif parameter == 4:
                parameter_reader = DviParser.read_signed_byte4
            elif parameter == -1:
                parameter_reader = DviParser.read_signed_byte1
            elif parameter == -2:
                parameter_reader = DviParser.read_signed_byte2
            elif parameter == -3:
                parameter_reader = DviParser.read_signed_byte3
                
            self.parameter_readers.append(parameter_reader)

    ###############################################

    def read_parameters(self, dvi_processor):

        parameters = []
        
        for parameter_reader in self.parameter_readers:
            parameters.append(parameter_reader(dvi_processor))
            
        return parameters

    ###############################################

    def to_opcode(self, parameters):

        if self.opcode_class is not None:
            return self.opcode_class(* parameters)
        else:
            return None

#####################################################################################################

class OpcodeParser_set_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_set_char, self).__init__(opcode, 'set', set_char_description,
                                                    opcode_class = Opcode_set_char)

    ###############################################

    def read_parameters(self, dvi_processor):

        return [self.opcode]

#####################################################################################################

class OpcodeParser_font(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_font, self).__init__(opcode, 'fnt num', 'set current font to i',
                                                opcode_class = Opcode_font)

    ###############################################

    def read_parameters(self, dvi_processor):

        return [self.opcode - FONT_00_OPCODE]

#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = 239

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'extension to DVI primitives',
                                               opcode_class = Opcode_xxx)

        self.read_unsigned_byten = DviParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_processor):

        return dvi_processor.read_stream(self.read_unsigned_byten(dvi_processor))

#####################################################################################################

class OpcodeParser_fnt_def(OpcodeParser):

    base_opcode = 243

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_fnt_def, self).__init__(opcode, 'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = DviParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_processor):

        font_id = self.read_unsigned_byten(dvi_processor)

        font_checksum     = dvi_processor.read_signed_byte4()
        font_scale_factor = dvi_processor.read_signed_byte4()
        font_design_size  = dvi_processor.read_signed_byte4()
        
        font_name = dvi_processor.read_stream(dvi_processor.read_unsigned_byte1() +
                                              dvi_processor.read_unsigned_byte1())

        dvi_processor.define_font(font_id, font_name, font_checksum, font_scale_factor, font_design_size)

#####################################################################################################

opcode_definitions = (
    ( [SETC_000_OPCODE, SETC_127_OPCODE], OpcodeParser_set_char ),
    ( SET1_OPCODE, 'set', set_char_description, ([1,4]), Opcode_set_char ),
    ( SET_RULE_OPCODE, 'set rule', 'typeset a rule and move right', (4,4), Opcode_set_rule ),
    ( PUT1_OPCODE, 'put', 'typeset a character', ([1,4]), Opcode_put_char ),
    ( PUT_RULE_OPCODE, 'put rule', 'typeset a rule', (4,4), Opcode_put_rule ),
    ( NOP_OPCODE, 'nop', 'no operation', None, None ),
    ( BOP_OPCODE, 'bop', 'beginning of page', tuple([4]*10), None ),
    ( EOP_OPCODE, 'eop', 'ending of page', None, None ),
    ( PUSH_OPCODE, 'push', 'save the current positions', None, Opcode_push ),
    ( POP_OPCODE, 'pop', 'restore previous positions', None, Opcode_pop ),
    ( RIGHT1_OPCODE, 'right', 'move right', ([1,4]), Opcode_right ),
    ( W0_OPCODE, 'w0', 'move right by w', None, Opcode_w0 ),
    ( W1_OPCODE, 'w', 'move right and set w', ([1,4]), Opcode_w ),
    ( X0_OPCODE, 'x0', 'move right by x', None, Opcode_x0 ),
    ( X1_OPCODE, 'x', 'move right and set x', ([1,4]), Opcode_x ),
    ( DOWN1_OPCODE, 'down', 'move down', ([1,4]), Opcode_down ),
    ( Y0_OPCODE, 'y0', 'move down by y', None, Opcode_y0 ),
    ( Y1_OPCODE, 'y', 'move down and set y', ([1,4]), Opcode_y ),
    ( Z0_OPCODE, 'z0', 'move down by z', None, Opcode_z0 ),
    ( Z1_OPCODE, 'z', 'move down and set z', ([1,4]), Opcode_z ),
    ( [FONT_00_OPCODE, FONT_63_OPCODE], OpcodeParser_font ),
    ( FNT1_OPCODE, 'fnt', 'set current font', ([1,4]), Opcode_font ),
    ( [XXX1_OPCODE, XXX4_OPCODE], OpcodeParser_xxx ),
    ( [FNT_DEF1_OPCODE, FNT_DEF4_OPCODE], OpcodeParser_fnt_def ),
    ( PRE_OPCODE, 'pre', 'preamble', (), None ),
    ( POST_OPCODE, 'post', 'postamble beginning', None, None ),
    ( POST_POST_OPCODE, 'post post', 'postamble ending', None, None ),
    )

for definition in opcode_definitions:

    index = definition[0]
    
    if isinstance(index, list):
        lower_index = index[0]
        upper_index = index[1]
    else:
        lower_index = upper_index = index

    if isinstance(definition[1], str):

        name, description, parameters, opcode_class = definition[1:]

        if parameters is not None and isinstance(parameters, list):
            lower_n, upper_n = parameters
            for n in xrange(lower_n, upper_n +1):
                i = index + n -1
                opcode_parsers[i] = OpcodeParser(i, name, description, tuple([n]), opcode_class)
        else:
            for i in xrange(lower_index, upper_index +1):
                opcode_parsers[i] = OpcodeParser(i, name, description, parameters, opcode_class)

    else:
        for i in xrange(lower_index, upper_index +1):
            opcode_parsers[i] = definition[1](i)

# for opcode_parsers in opcode_parsers:
#     print opcode_parsers

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

    dvi_stream = open(dvi_file)

    dvi_parser = DviParser()

    dvi_parser.process_stream(dvi_stream)

    dvi_parser.print_summary()

    dvi_machine = DviMachine()

    print '\nRun last page'
    dvi_machine.run(dvi_parser.page_opcode_programs[-1])

    dvi_stream.close()

#####################################################################################################
#
# End
#
#####################################################################################################
