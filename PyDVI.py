#####################################################################################################


#####################################################################################################

DVI_FORMAT = 2
DVIV_FORMAT = 3
XDVI_FORMAT = 5

NOP_OPCODE = 138
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

# opcodes =

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

    def read_unsigned_byte4(self):
        return self.read_big_endian_number(4, signed = False)

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

        self.numerator     = self.read_unsigned_byte4()
        self.denominator   = self.read_unsigned_byte4()
        self.magnification = self.read_unsigned_byte4()

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
        self.post_pointer = self.read_unsigned_byte4()

        # Move to post
        self.stream.seek(self.post_pointer)

        if self.read_unsigned_byte1() != POST_OPCODE:
            raise NameError('Bad DVI stream')            

        self.bop_pointer_stack.append(self.read_unsigned_byte4())

        numerator     = self.read_unsigned_byte4()
        denominator   = self.read_unsigned_byte4()
        magnification = self.read_unsigned_byte4()

        self.max_height = self.read_unsigned_byte4()
        self.max_width  = self.read_unsigned_byte4()
        self.stack_depth = self.read_unsigned_byte2()
        self.number_of_pages = self.read_unsigned_byte2()

        # Read Font definition

        while True:

            opcode = self.read_unsigned_byte1()

            if   opcode == FNT_DEF1_OPCODE: font_id = self.read_unsigned_byte1()
            elif opcode == FNT_DEF2_OPCODE: font_id = self.read_unsigned_byte2()
            elif opcode == FNT_DEF3_OPCODE: font_id = self.read_unsigned_byte3()
            elif opcode == FNT_DEF4_OPCODE: font_id = self.read_unsigned_byte4()
            elif opcode != NOP_OPCODE: break

            self.define_font(font_id)

        if opcode != POST_POST_OPCODE:
            raise NameError('Bad DVI stream')

        post_pointer = self.read_unsigned_byte4()
        dvi_format = self.read_unsigned_byte1()

    ###############################################

    def define_font(self, font_id):

        font_checksum     = self.read_unsigned_byte4()
        font_scale_factor = self.read_unsigned_byte4()
        font_design_size  = self.read_unsigned_byte4()
        
        font_name = self.read_stream(self.read_unsigned_byte1() + self.read_unsigned_byte1())

        self.fonts[font_id] = {'name':font_name,
                               'checksum':font_checksum,
                               'scale_factor':font_scale_factor,
                               'design_size':font_design_size}

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
