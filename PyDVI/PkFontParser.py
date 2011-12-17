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
#  - 17/01/2010 fabrice
#
#####################################################################################################

"""
The PkFontParser module provides a tool to parse Packet Font files.  PK files contain device
dependent bitmap fonts.  They have the ".pk" extension.
"""

#####################################################################################################

__all__ = ['PkFontParser', 'OpcodeParser_xxx']

#####################################################################################################

import sys

#####################################################################################################

from PyDVI.OpcodeParser import OpcodeParserSet, OpcodeParser
from PyDVI.PkGlyph import PkGlyph
from PyDVI.TeXUnit import *
from PyDVI.Tools.EnumFactory import ExplicitEnumFactory
from PyDVI.Tools.Logging import print_card
from PyDVI.Tools.Stream import to_fix_word, AbstractStream, FileStream

#####################################################################################################

def repeat(func, number_of_times):
    return [func() for i in xrange(number_of_times)]

#####################################################################################################

pk_opcodes = ExplicitEnumFactory('PkOpcodes', {
        'XXX1':240,
        'XXX2':241,
        'XXX3':242,
        'XXX4':243,
        'YYY':244,
        'POST':245,
        'NOP':246,
        'PRE':247
        })

PK_ID = 89
           
#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = pk_opcodes.XXX1

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'special')

        self.read_unsigned_byten = AbstractStream.read_unsigned_byten[opcode - self.base_opcode]

    ###############################################

    def read_parameters(self, pk_font_parser):

        stream = pk_font_parser.stream

        return stream.read(self.read_unsigned_byten(stream))

#####################################################################################################

opcode_definitions = (
    ( pk_opcodes.NOP, 'nop', 'no operation', None, None ),
    ( [pk_opcodes.XXX1,
       pk_opcodes.XXX4], OpcodeParser_xxx ),
    ( pk_opcodes.YYY, 'yyy', 'numspecial', (4,), None ),
    ( pk_opcodes.PRE, 'pre', 'preamble', (), None ), # Fixme: pre is not used in the loop
    ( pk_opcodes.POST, 'post', 'postamble', None, None ),
    )

class PkFontParser(object):

    opcode_parser_set = OpcodeParserSet(opcode_definitions)

    ###############################################

    @staticmethod
    def parse(pk_font):

        PkFontParser(pk_font)

    ###############################################

    def __init__(self, pk_font):

        self.pk_font = pk_font

        self.stream = FileStream(pk_font.filename)

        self._process_preambule()
        self._process_file()

    ###############################################

    def _process_preambule(self):

        """ Process the preamble. """

        stream = self.stream

        stream.seek(0)

        if stream.read_unsigned_byte1() != pk_opcodes.PRE:
            raise NameError("PK file don't start by PRE opcode")

        pk_id = stream.read_unsigned_byte1()
        if pk_id != PK_ID:
            raise NameError("Unknown PK ID")

        comment = stream.read(stream.read_unsigned_byte1())
        design_font_size = stream.read_fix_word()
        checksum = stream.read_signed_byte4()
        horizontal_dpi = sp2dpi(stream.read_signed_byte4())
        vertical_dpi = sp2dpi(stream.read_signed_byte4())

        string_template = '''
Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design size  %.1f pt
  - Checksum     %u
  - Resolution
   - Horizontal  %.1f dpi
   - Vertical    %.1f dpi '''

        print string_template % (
            pk_id,
            comment,
            design_font_size,
            checksum,
            horizontal_dpi,
            vertical_dpi,
            )
        
        self.pk_font._set_preambule_data(pk_id, comment, design_font_size, checksum,
                                         horizontal_dpi, vertical_dpi)

    ###############################################

    def _process_file(self):

        """ Process the characters. """
        
        stream = self.stream

        # Fixme: to incorporate pre, check here pre is the first code

        while True:
            byte = stream.read_unsigned_byte1()
            if byte == pk_opcodes.POST:
                break
            elif byte >= pk_opcodes.XXX1:
                # Fixme: self.opcode_parsers[byte]()
                opcode_parser = self.opcode_parser_set[byte]
                opcode_parser.read_parameters(self) # Fixme: return where
            else:
                self._read_char_definition(byte)

    ###############################################

    def _read_char_definition(self, flag):

        stream = self.stream

        dyn_f = flag >> 4
        first_pixel_is_black = (flag & 8) != 0
        two_bytes = (flag & 4) != 0

        three_least_significant = flag & 7
        two_least_significant = flag & 3

        if three_least_significant <= 3: # bit 2**3 is not set
            format = 1 # short form
        elif three_least_significant == 7: # all 3-bit are set
            format = 3 # long form
        else: # 3 < 3-bit < 7, bit 2**3 is set
            format = 2 # extended form

        # preambule_length is counted next to packed_length

        if format == 1:
            # (flag mod 4)*256 + pl
            packet_length = (two_least_significant << 8) + stream.read_unsigned_byte1()
            preambule_length = 8 # 3 + 1*5
        elif format == 2:
            packet_length = (two_least_significant << 16) + stream.read_unsigned_byte2()
            preambule_length = 13 # 3 + 2*5
        else:
            packet_length = stream.read_unsigned_byte4()
            preambule_length = 28 # 4*7

        if format == 3:
            (char_code, tfm,
             dx, dy,
             width, height,
             horizontal_offset, vertical_offset) = repeat(stream.read_unsigned_byte4, 8)
            dm = None
 
        else:
            if format == 1:
                read_unsigned_byte = stream.read_unsigned_byte1
                read_signed_byte = stream.read_signed_byte1
            else:
                read_unsigned_byte = stream.read_unsigned_byte2
                read_signed_byte = stream.read_signed_byte2

            char_code = stream.read_unsigned_byte1()
            tfm = stream.read_unsigned_byte3()
            (dm, width, height) = repeat(read_unsigned_byte, 3)
            (horizontal_offset, vertical_offset) = repeat(read_signed_byte, 2)
            dx = dm
            dy = 0

        tfm = to_fix_word(tfm)

        nybbles = stream.read(packet_length - preambule_length)

        PkGlyph(self.pk_font,
                char_code,
                tfm, dm, dx, dy,
                height, width,
                horizontal_offset, vertical_offset,
                nybbles, dyn_f, first_pixel_is_black)

        if False:
            string_template = '''Char %u
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
'''

            print_card(string_template % (
                    char_code,
                    flag, dyn_f, first_pixel_is_black, two_bytes, format, packet_length,
                    tfm, dm, dx, dy,
                    height, width,
                    horizontal_offset, vertical_offset,
                    ))

#####################################################################################################
#
# End
#
#####################################################################################################
