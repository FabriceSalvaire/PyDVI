#####################################################################################################

#####################################################################################################

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

#####################################################################################################

DVI_FORMAT = 2
DVIV_FORMAT = 3
XDVI_FORMAT = 5

# Fixme: use opcode_definitions?
NOP_OPCODE = 138
BOP_OPCODE = 139
EOP_OPCODE = 140
FNT_OPCODE = 171
FNT_DEF1_OPCODE = 243
FNT_DEF4_OPCODE = 246
PRE_OPCODE = 247
POST_OPCODE = 248
POST_POST_OPCODE = 249

EOF_SIGNATURE = 223

opcode_objects = [None]*255

#####################################################################################################

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
        self.print_object()
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
            if opcode >= FNT_DEF1_OPCODE and opcode <= FNT_DEF4_OPCODE:
                opcode_objects[opcode].read_parameters(self)
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

        bop_pointer = self.bop_pointer_stack[0]

        while bop_pointer >= 0:

            self.stream.seek(bop_pointer)

            opcode = self.read_unsigned_byte1()

            if opcode != BOP_OPCODE:
                raise NameError('Bad DVI stream')

            counts = [self.read_signed_byte4() for i in xrange(10)]

            print '\nPage', counts

            bop_pointer = self.read_signed_byte4()

            self.bop_pointer_stack.append(bop_pointer)

            page = self.process_page()

    ###############################################

    def process_page(self):

        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == EOP_OPCODE:
                break
            else:
                opcode_obj = opcode_objects[opcode]

                opcode_obj.read_parameters(self)

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
            print 'id = %4u' % (font_id), self.fonts[font_id]

    ###############################################

    read_unsigned_byten_pointer = (read_unsigned_byte1, 
                                   read_unsigned_byte2,
                                   read_unsigned_byte3,
                                   read_signed_byte4)

#####################################################################################################

class Opcode(object):

    ###############################################

    def __init__(self, opcode, name, description, parameters = ()):

        self.opcode = opcode
        self.name = name
        self.description = description

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
                parameter_reader = DviProcessor.read_unsigned_byte1
            elif parameter == 2:
                parameter_reader = DviProcessor.read_unsigned_byte2
            elif parameter == 3:
                parameter_reader = DviProcessor.read_unsigned_byte3
            elif parameter == 4:
                parameter_reader = DviProcessor.read_signed_byte4
            elif parameter == -1:
                parameter_reader = DviProcessor.read_signed_byte1
            elif parameter == -2:
                parameter_reader = DviProcessor.read_signed_byte2
            elif parameter == -3:
                parameter_reader = DviProcessor.read_signed_byte3
                
            self.parameter_readers.append(parameter_reader)

    ###############################################

    def read_parameters(self, dvi_processor):

        parameters = []

        for parameter_reader in self.parameter_readers:
            parameters.append(parameter_reader(dvi_processor))
            
        if self.name == 'fnt num':
            print self.name, self.opcode - FNT_OPCODE
        elif self.opcode < 128:
            print self.name, chr(self.opcode)
        else:
            print self.name, self.opcode, parameters

        return parameters

#####################################################################################################

class Opcode_xxx(Opcode):

    base_opcode = 239

    ###############################################

    def __init__(self, opcode):

        super(Opcode_xxx, self).__init__(opcode, 'xxx', 'extension to DVI primitives')

        self.read_unsigned_byten = DviProcessor.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_processor):

        return dvi_processor.read_stream(self.read_unsigned_byten(dvi_processor))

#####################################################################################################

class Opcode_fnt_def(Opcode):

    base_opcode = 243

    ###############################################

    def __init__(self, opcode):

        super(Opcode_fnt_def, self).__init__(opcode, 'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = DviProcessor.read_unsigned_byten_pointer[opcode-self.base_opcode]

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

set_description = 'typeset a character and move right'

opcode_definitions = (
    ( [0, 127], 'set', set_description, None ),
    ( 128, 'set', set_description, ([1,4]) ),
    ( 132, 'set rule', 'typeset a rule and move right', (4,4) ),
    ( 133, 'put', 'typeset a character', ([1,4]) ),
    ( 137, 'put rule', 'typeset a rule', (4,4) ),
    ( 138, 'nop', 'no operation', None ),
    ( 139, 'bop', 'beginning of page', tuple([4]*10) ),
    ( 140, 'eop', 'ending of page', None ),
    ( 141, 'push', 'save the current positions', None ),
    ( 142, 'pop', 'restore previous positions', None ),
    ( 143, 'right', 'move right', ([1,4]) ),
    ( 147, 'w0', 'move right by w', None ),
    ( 148, 'w', 'move right and set w', ([1,4]) ),
    ( 152, 'x0', 'move right by x', None ),
    ( 153, 'x', 'move right and set x', ([1,4]) ),
    ( 157, 'down', 'move down', ([1,4]) ),
    ( 161, 'y0', 'move down by y', None ),
    ( 162, 'y', 'move down and set y', ([1,4]) ),
    ( 166, 'z0', 'move down by z', None ),
    ( 167, 'z', 'move down and set z', ([1,4]) ),
    ( [171, 234], 'fnt num', 'set current font to i', None ),
    ( 235, 'fnt', 'set current font', ([1,4]) ),
    ( [239, 242], Opcode_xxx ),
    ( [243, 246], Opcode_fnt_def ),
    ( 247, 'pre', 'preamble', () ),
    ( 248, 'post', 'postamble beginning', None ),
    ( 249, 'post post', 'postamble ending', None ),
    # [250, 255]
    )

for definition in opcode_definitions:

    index = definition[0]
    
    if isinstance(index, list):
        lower_index = index[0]
        upper_index = index[1]
    else:
        lower_index = upper_index = index

    if isinstance(definition[1], str):

        name, description, parameters = definition[1:]

        if parameters is not None and isinstance(parameters, list):
            lower_n, upper_n = parameters
            for n in xrange(lower_n, upper_n +1):
                i = index + n -1
                opcode_objects[i] = Opcode(i, name, description, tuple([n]))
        else:
            for i in xrange(lower_index, upper_index +1):
                opcode_objects[i] = Opcode(i, name, description, parameters)

    else:
        for i in xrange(lower_index, upper_index +1):
            opcode_objects[i] = definition[1](i)

# for opcode_object in opcode_objects:
#     print opcode_object

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

    dvi_stream.close()

#####################################################################################################
#
# End
#
#####################################################################################################
