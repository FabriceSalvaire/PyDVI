#####################################################################################################

import string

#####################################################################################################

from OpcodeParser import *

#####################################################################################################

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

#####################################################################################################

PK_ID = 89

CHAR_000_OPCODE = 0
CHAR_239_OPCODE = 239
XXX1_OPCODE     = 240
XXX3_OPCODE     = 241
XXX2_OPCODE     = 242
XXX4_OPCODE     = 243
YYY_OPCODE      = 244
POST_OPCODE     = 245
NOP_OPCODE      = 246
PRE_OPCODE      = 247

#####################################################################################################

class OpcodeParser_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_char, self).__init__(opcode, 'char', '')

    ###############################################

    def read_parameters(self, dvi_processor):

        print hex(dvi_processor.read_unsigned_byte1())
        print hex(dvi_processor.read_unsigned_byte1())
        print hex(dvi_processor.read_unsigned_byte1())
        print hex(dvi_processor.read_unsigned_byte1())

        flag = self.opcode # dvi_processor.read_unsigned_byte1()

        dyn_f = flag >> 4
        black_count = (flag & 8) != 0
        two_bytes =  (flag & 4) != 0

        three_least_significant = flag & 7
        two_least_significant = flag & 3

        if three_least_significant <= 3:
            format = 1
        elif three_least_significant == 7:
            format = 3
        else:
            format = 2

        if format == 1:
            packet_length = two_least_significant << 8 + dvi_processor.read_unsigned_byte1()
        elif format == 2:
            packet_length = two_least_significant << 16 + dvi_processor.read_unsigned_byte2()
        else:
            packet_length = two_least_significant << 32 + dvi_processor.read_unsigned_byte4()

        print '''
Char %u
 - Flag: %u
 - Dynamic Packing Variable: %u
 - Black Count: %s
 - Two Bytes: %s
 - Format: %u
 - Packet Length: %u

 - TFM width:
 - dx:
 - Height:
 - Width:
 - X-offset:
 - Y-offset:
''' % (self.opcode, flag,  dyn_f, black_count, two_bytes, format, packet_length)

        dvi_processor.read_stream(packet_length)

        return [self.opcode]

#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = XXX1_OPCODE

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'special')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_processor):

        return dvi_processor.read_stream(self.read_unsigned_byten(dvi_processor))

#####################################################################################################

class PkFont(OpcodeStreamParser):

    opcode_definitions = (
        ( [CHAR_000_OPCODE, CHAR_239_OPCODE], OpcodeParser_char ),
        ( NOP_OPCODE, 'nop', 'no operation', None, None ),
        ( [XXX1_OPCODE, XXX4_OPCODE], OpcodeParser_xxx ),
        ( YYY_OPCODE, 'yyy', 'numspecial', tuple([4]), None ),
        ( PRE_OPCODE, 'pre', 'preamble', (), None ),
        ( POST_OPCODE, 'post', 'postamble', None, None ),
        )
   
    ###############################################

    def __init__(self, pk_file_name):

        super(PkFont, self).__init__(self.opcode_definitions)

        self.pk_file_name = pk_file_name

        stream = open(pk_file_name)

        self.set_stream(stream)

        self.process_preambule()
        self.process_characters()

        self.set_stream(None)

        stream.close()

    ###############################################

    def process_preambule(self):

        self.stream.seek(0)

        if self.read_unsigned_byte1() != PRE_OPCODE:
            raise NameError('Bad PK File')

        self.pk_id = self.read_unsigned_byte1()
        if self.pk_id != PK_ID:
            raise NameError('Bad PK File')

        self.comment = self.read_stream(self.read_unsigned_byte1())

        self.design_size = self.read_signed_byte4()
        self.checksum = self.read_signed_byte4()
        self.horizontal_pixels_per_point = self.read_signed_byte4()
        self.vertical_pixels_per_point = self.read_signed_byte4()

    ###############################################

    def process_characters(self):
        
        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == POST_OPCODE:
                break
            else:
                opcode_parser = self.opcode_parsers[opcode]

                parameters = opcode_parser.read_parameters(self)

                print opcode_parser, parameters

    ###############################################

    def print_summary(self):

        print '''PK File %s

Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design Size  %u
  - Checksum     %u
  - Horizontal Pixels per Point %u
  - Vertical   Pixels per Point %u
  ''' % (self.pk_file_name,
         self.pk_id,
         self.comment,
         self.design_size,
         self.checksum,
         self.horizontal_pixels_per_point,
         self.vertical_pixels_per_point)

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

    pk_file_name = args[0]

    pk_font = PkFont(pk_file_name)

    pk_font.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
