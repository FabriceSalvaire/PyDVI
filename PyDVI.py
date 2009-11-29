#####################################################################################################


#####################################################################################################

DVI_FORMAT = 2
DVIV_FORMAT = 3
XDVI_FORMAT = 5

PRE_OPCODE = 247

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

    ###############################################

    def process_stream(self, stream):

        self.stream = stream

        self.reset()

        self.process_preambule()

    ###############################################

    def read_stream(self, n):

        '''Read the DVI input stream

        n > 0, exception ...
        '''

        return self.stream.read(n)

    def get_big_endian_number(self, n, signed = False):

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
            
    def get_unsigned_byte1(self):
        return self.get_big_endian_number(1, signed = False)

    def get_signed_byte1(self):
        return self.get_big_endian_number(1, signed = True)

    def get_unsigned_byte2(self):
        return self.get_big_endian_number(2, signed = False)

    def get_signed_byte2(self):
        return self.get_big_endian_number(2, signed = True)

    def get_unsigned_byte3(self):
        return self.get_big_endian_number(3, signed = False)

    def get_signed_byte3(self):
        return self.get_big_endian_number(3, signed = True)

    def get_unsigned_byte4(self):
        return self.get_big_endian_number(4, signed = False)

    def get_signed_byte4(self):
        return self.get_big_endian_number(4, signed = True)

    ###############################################

    def process_preambule(self):

        # self.stream.seek(0)

        if self.get_unsigned_byte1() != PRE_OPCODE:
            raise NameError('Bad DVI stream')

        self.dvi_id = self.get_unsigned_byte1()
        if self.dvi_id not in (DVI_FORMAT, DVIV_FORMAT, XDVI_FORMAT):
            raise NameError('Bad DVI Format')

        self.numerator     = self.get_unsigned_byte4()
        self.denominator   = self.get_unsigned_byte4()
        self.magnification = self.get_unsigned_byte4()

        self.comment = self.read_stream(self.get_unsigned_byte1())

    ###############################################

    def print_object(self):

        print '''
Preambule
  - DVI Format    %u
  - Numerator     %u
  - Denominator   %u
  - Magnification %u
  - Comment       '%s'
''' % (self.dvi_format, self.numerator, self.denominator, self.magnification, self.comment)

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
