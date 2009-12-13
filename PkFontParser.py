#####################################################################################################

import sys
import string

#####################################################################################################

from OpcodeParser import *
from PkGlyph import PkGlyph
from TeXUnit import sp2in

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

    def read_parameters(self, pk_font_parser):

        flag = self.opcode

        dyn_f = flag >> 4
        first_pixel_is_black = (flag & 8) != 0
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
            # (flag mod 4)*256 + pl
            packet_length = (two_least_significant << 8) + pk_font_parser.read_unsigned_byte1()
            preambule_length = 3 + 5
        elif format == 2:
            packet_length = (two_least_significant << 16) + pk_font_parser.read_unsigned_byte2()
            preambule_length = 3 + 5*2
        else:
            packet_length = pk_font_parser.read_unsigned_byte4()
            preambule_length = 7*4

        if format == 3:
            (char_code, tfm,
             dx, dy,
             width, height,
             horizontal_offset, vertical_offset) = [pk_font_parser.read_unsigned_byte4() for i in xrange(8)]
            dm = None
        else:
            char_code = pk_font_parser.read_unsigned_byte1()
            tfm = pk_font_parser.read_unsigned_byte3()
            if format == 1:
                (dm, width, height) = [pk_font_parser.read_unsigned_byte1() for i in xrange(3)]
                (horizontal_offset, vertical_offset) = [pk_font_parser.read_signed_byte1() for i in xrange(2)]
            else:
                (dm, width, height) = [pk_font_parser.read_unsigned_byte2() for i in xrange(3)]
                (horizontal_offset, vertical_offset) = [pk_font_parser.read_signed_byte2() for i in xrange(2)]
            dx = dm
            dy = 0

        nybbles = pk_font_parser.read_stream(packet_length-preambule_length)

        PkGlyph(pk_font_parser.pk_font,
                char_code,
                tfm, dm, dx, dy,
                height, width,
                horizontal_offset, vertical_offset,
                nybbles, dyn_f, first_pixel_is_black)

        if False:
            print '''
Char %u
 - Flag: %u
 - Dynamic Packing Variable: %u
 - First pixel is black: %s
 - Two Bytes: %s
 - Format: %u
 - Packet Length: %u
 - TFM width: %u
 - dm: %u
 - dx: %u
 - dy: %u
 - Height: %u
 - Width: %u
 - Horizontal Offset: %u
 - Vertical Offset: %u
''' % (char_code,
       flag, dyn_f, first_pixel_is_black, two_bytes, format, packet_length,
       tfm, dm, dx, dy,
       height, width,
       horizontal_offset, vertical_offset)
        
#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = XXX1_OPCODE

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'special')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, pk_font_parser):

        return pk_font_parser.read_stream(self.read_unsigned_byten(pk_font_parser))

#####################################################################################################

class PkFontParser(OpcodeStreamParser):

    opcode_definitions = (
        ( [CHAR_000_OPCODE, CHAR_239_OPCODE], OpcodeParser_char ),
        ( NOP_OPCODE, 'nop', 'no operation', None, None ),
        ( [XXX1_OPCODE, XXX4_OPCODE], OpcodeParser_xxx ),
        ( YYY_OPCODE, 'yyy', 'numspecial', tuple([4]), None ),
        ( PRE_OPCODE, 'pre', 'preamble', (), None ),
        ( POST_OPCODE, 'post', 'postamble', None, None ),
        )
   
    ###############################################

    def __init__(self):

        super(PkFontParser, self).__init__(self.opcode_definitions)

        self.pk_font = None

    ###############################################

    def process_pk_font(self, pk_font):

        self.pk_font = pk_font

        stream = open(pk_font.font_file_name)

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

        pk_id = self.read_unsigned_byte1()
        if pk_id != PK_ID:
            raise NameError('Bad PK File')

        self.pk_font.set_preambule_data(pk_id = pk_id,
                                        comment = self.read_stream(self.read_unsigned_byte1()),
                                        design_size = float(self.read_signed_byte4())/2**20,
                                        checksum = self.read_signed_byte4(),
                                        horizontal_pixels_per_point = sp2in(self.read_signed_byte4()),
                                        vertical_pixels_per_point = sp2in(self.read_signed_byte4()))

    ###############################################

    def process_characters(self):
        
        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == POST_OPCODE:
                break

            else:
                opcode_parser = self.opcode_parsers[opcode]

                opcode_parser.read_parameters(self)

#####################################################################################################
#
# End
#
#####################################################################################################
