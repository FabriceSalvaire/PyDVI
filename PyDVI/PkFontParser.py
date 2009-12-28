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
#  - 19/12/2009 fabrice
#
#####################################################################################################

#####################################################################################################

import sys
import string

#####################################################################################################

from EnumFactory import *
from Stream import *
from OpcodeParser import *
from PkGlyph import PkGlyph
from TeXUnit import *

#####################################################################################################

pk_opcodes_tuple = []

for i in xrange(240):
    pk_opcodes_tuple.append('CHAR_%03u' % (i))

pk_opcodes_tuple += [
    'XXX1', 'XXX3', 'XXX2', 'XXX4',
    'YYY',
    'POST',
    'NOP',
    'PRE',
    ]

pk_opcodes = EnumFactory('PkOpcodes', pk_opcodes_tuple)

PK_ID = 89

#####################################################################################################

class OpcodeParser_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_char, self).__init__(opcode,
                                                'char', '')

    ###############################################

    def read_parameters(self, pk_font_parser):

        flag = self.opcode

        dyn_f = flag >> 4
        first_pixel_is_black = (flag & 8) != 0
        two_bytes = (flag & 4) != 0

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
            preambule_length = 3 + 2*5
        else:
            packet_length = pk_font_parser.read_unsigned_byte4()
            preambule_length = 4*7

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
                read_unsigned_byte = pk_font_parser.read_unsigned_byte1
                read_signed_byte = pk_font_parser.read_signed_byte1
            else:
                read_unsigned_byte = pk_font_parser.read_unsigned_byte2
                read_signed_byte = pk_font_parser.read_signed_byte2

            (dm, width, height) = [read_unsigned_byte() for i in xrange(3)]
            (horizontal_offset, vertical_offset) = [read_signed_byte() for i in xrange(2)]

            dx = dm
            dy = 0


        tfm = pk_font_parser.to_fix_word(tfm)

        nybbles = pk_font_parser.read(packet_length - preambule_length)

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

    base_opcode = pk_opcodes.XXX1

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode,
                                               'xxx', 'special')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten[opcode - self.base_opcode]

    ###############################################

    def read_parameters(self, pk_font_parser):

        return pk_font_parser.read(self.read_unsigned_byten(pk_font_parser))

#####################################################################################################

class PkFontParser(OpcodeStreamParser, FileStream):

    opcode_definitions = (
        ( [pk_opcodes.CHAR_000,
           pk_opcodes.CHAR_239], OpcodeParser_char ),
        ( pk_opcodes.NOP, 'nop', 'no operation', None, None ),
        ( [pk_opcodes.XXX1,
           pk_opcodes.XXX4], OpcodeParser_xxx ),
        ( pk_opcodes.YYY, 'yyy', 'numspecial', (4,), None ),
        ( pk_opcodes.PRE, 'pre', 'preamble', (), None ),
        ( pk_opcodes.POST, 'post', 'postamble', None, None ),
        )
   
    ###############################################

    def __init__(self):

        super(PkFontParser, self).__init__(self.opcode_definitions)

        self.pk_font = None

    ###############################################

    def process_pk_font(self, pk_font):

        self.pk_font = pk_font

        self.open(pk_font.filename)

        self.process_preambule()
        self.process_characters()

        self.close()

    ###############################################

    def process_preambule(self):

        self.seek(0)

        if self.read_unsigned_byte1() != pk_opcodes.PRE:
            raise NameError("PK file don't start by PRE")

        pk_id = self.read_unsigned_byte1()
        if pk_id != PK_ID:
            raise NameError("Unknown PK ID")

        self.pk_font.set_preambule_data(pk_id = pk_id,
                                        comment = self.read(self.read_unsigned_byte1()),
                                        design_size = self.read_fix_word(),
                                        checksum = self.read_signed_byte4(),
                                        horizontal_dpi = sp2dpi(self.read_signed_byte4()),
                                        vertical_dpi = sp2dpi(self.read_signed_byte4()))

    ###############################################

    def process_characters(self):
        
        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == pk_opcodes.POST:
                break

            else:
                opcode_parser = self.opcode_parsers[opcode]

                opcode_parser.read_parameters(self)

#####################################################################################################
#
# End
#
#####################################################################################################
