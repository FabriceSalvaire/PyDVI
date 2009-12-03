#####################################################################################################

#####################################################################################################

class Opcode(object):

    def __init__(self, opcode, name, description, parameters):

        self.opcode = opcode
        self.name = name
        self.description = description

        for parameter in parameters

#####################################################################################################

DVI_FORMAT = 2
DVIV_FORMAT = 3
XDVI_FORMAT = 5

# use opcode_definitions
NOP_OPCODE = 138
BOP_OPCODE = 139
FNT_DEF1_OPCODE = 243
FNT_DEF2_OPCODE = 244
FNT_DEF3_OPCODE = 245
FNT_DEF4_OPCODE = 246
PRE_OPCODE = 247
POST_OPCODE = 248
POST_POST_OPCODE = 249

EOF_SIGNATURE = 223

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

opcode_definitions = (
    ( [0, 127], 'set', 'typeset a character and move right', None ),
    ( 128, 'set', 'typeset a character and move right', ([1,4]) ),
    ( 132, 'set rule', 'typeset a rule and move right', (4,4) ),
    ( 133, 'put', 'typeset a character', ([1,4]) ),
    ( 137, 'put rule', 'typeset a rule', (4,4) ),
    ( 138, 'nop', 'no operation', None ),
    ( 139, 'bop', 'beginning of page', () ),
    ( 140, 'eop', 'ending of page', None ),
    ( 141, 'push', 'save the current positions', None ),
    ( 142, 'pop', 'restore previous positions', None ),
    ( 143, 'right', 'move right', ([1,4]) ),
    ( 147, 'w0', 'move right by w', None ),
    ( 147, 'w', 'move right and set w', ([1,4]) ),
    ( 152, 'x0', 'move right by x', None ),
    ( 152, 'x', 'move right and set x', ([1,4]) ),
    ( 157, 'down', 'move down', ([1,4]) ),
    ( 161, 'y0', 'move down by y', None ),
    ( 162, 'y', 'move down and set y', ([1,4]) ),
    ( 166, 'z0', 'move down by z', None ),
    ( 167, 'z', 'move down and set z', ([1,4]) ),
    ( [171, 234], 'fnt num', 'set current font to i', None ),
    ( 235, 'fnt', 'set current font', ([1,4]) ),
    ( 239, 'xxx', 'extension to DVI primitives' ),
    ( 243, 'fnt def', 'define the meaning of a font number', () ),
    ( 247, 'pre', 'preamble', () ),
    ( 248, 'post', 'postamble beginning', None ),
    ( 249, 'post post', 'postamble ending', None ),
    # [250, 255]
    )

opcodes_callback = [None]*255

for definition in opcode_definition:

    index, name, description, parameters = definition

    if isinstance(index, list):

        for i in xrange(index[0], index[1] +1):
            opcodes_callback[i] = (definition, parameters)

    else:

        if len(parameters) > 0 and isinstance(parameters[0], list):
            for i in xrange(parameters[0][0], parameters[0][1] +1):
                opcodes_callback[index] = (definition, (i))
        else:
            opcodes_callback[index] = (definition, parameters)

class DviProcessor(object):
   
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

        self.bop_pointer_stack = []

        self.fonts = {}

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
            number <<= 8
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

            if   opcode == FNT_DEF1_OPCODE: font_id = self.read_unsigned_byte1()
            elif opcode == FNT_DEF2_OPCODE: font_id = self.read_unsigned_byte2()
            elif opcode == FNT_DEF3_OPCODE: font_id = self.read_unsigned_byte3()
            elif opcode == FNT_DEF4_OPCODE: font_id = self.read_signed_byte4()
            elif opcode != NOP_OPCODE: break

            self.define_font(font_id)

        # POST POST

        if opcode != POST_POST_OPCODE:
            raise NameError('Bad DVI stream')

        post_pointer = self.read_signed_byte4()
        dvi_format = self.read_unsigned_byte1()

    ###############################################

    def define_font(self, font_id):

        font_checksum     = self.read_signed_byte4()
        font_scale_factor = self.read_signed_byte4()
        font_design_size  = self.read_signed_byte4()
        
        font_name = self.read_stream(self.read_unsigned_byte1() + self.read_unsigned_byte1())

        self.fonts[font_id] = {'name':font_name,
                               'checksum':font_checksum,
                               'scale_factor':font_scale_factor,
                               'design_size':font_design_size}

    ###############################################

    def process_pages(self):

        bop_pointer = self.bop_pointer_stack[0]

        while loc >= 0:

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

        while True:

            opcode = self.read_unsigned_byte1()

            definition, parameters = opcodes_callback[opcode]

            for parameter in parameters:

    ###############################################

    def print_object(self):

        print '''
Preambule
  - DVI format    %u
  - numerator     %u
  - denominator   %u
  - magnification %u
  - comment       '%s'

Postamble
  - pointer         %u
  - max height      %u
  - max width       %u
  - stack depth     %u
  - number of pages %u

Fonts
''' % (self.dvi_format, self.numerator, self.denominator, self.magnification, self.comment,
       self.post_pointer, self.max_height, self.max_width, self.stack_depth, self.number_of_pages)

        for font_id in self.fonts.keys():
            print self.fonts[font_id]

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

    dvi_processor = DviProcessor()

    dvi_processor.process_stream(dvi_stream)

    dvi_processor.print_object()

    dvi_stream.close()

#####################################################################################################
#
# End
#
#####################################################################################################
