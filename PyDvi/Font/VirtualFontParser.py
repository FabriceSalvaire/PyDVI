####################################################################################################
# 
# PyDvi - A Python Library to Process DVI Stream
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
####################################################################################################

"""The VirtualFontParser module provides a tool to parse virtual font files.  They have the ".vf"
extension.

"""

####################################################################################################

__all__ = ['VirtualFontParser']

####################################################################################################

import logging

####################################################################################################

from ..Dvi.DviMachine import DviFont
from ..OpcodeParser import OpcodeParserSet, OpcodeParser
from ..Tools.EnumFactory import EnumFactory
from ..Tools.Stream import to_fix_word, AbstractStream, FileStream
from .VirtualCharacter import VirtualCharacter

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

vf_opcodes_tuple = ['SHORT_CHAR_%03u' % (i) for i in xrange(242)]

vf_opcodes_tuple += [
    'LONG_CHAR', # 242
    'FNT_DEF1', 'FNT_DEF2', 'FNT_DEF3', 'FNT_DEF4', # 243 to 246
    'PRE', # 247
    'POST', # 248
    ]

vf_opcodes = EnumFactory('VfOpcodes', vf_opcodes_tuple)

VF_ID = 202

####################################################################################################

class OpcodeParser_char(OpcodeParser):

    """ This class parse the ``char`` opcode. """

    _logger = _module_logger.getChild('OpcodeParser_char')

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_char, self).__init__(opcode,
                                                'char', 'define a virtual character number')

        self._long_char = opcode == vf_opcodes.LONG_CHAR

    ##############################################

    def read_parameters(self, virtual_font_parser):

        stream = virtual_font_parser.stream

        self._logger.debug("opcode {}".format(self.opcode))

        if self._long_char:
            dvi_length = stream.read_unsigned_byte4()
            char_code = stream.read_unsigned_byte4()
            width = stream.read_unsigned_byte4()
        else:
            dvi_length = self.opcode
            char_code = stream.read_unsigned_byte1()
            width = stream.read_unsigned_byte3()
        dvi = stream.read(dvi_length)

        character = VirtualCharacter(char_code, width, dvi)
        virtual_font_parser.virtual_font.register_character(character)

####################################################################################################

class OpcodeParser_fnt_def(OpcodeParser):

    """ This class parse the ``fnt_def`` opcode. """

    # The code is identical to one of DviParser.

    base_opcode = vf_opcodes.FNT_DEF1

    ##############################################

    def __init__(self, opcode):

        super(OpcodeParser_fnt_def, self).__init__(opcode,
                                                   'fnt def', 'define the meaning of a font number')

        self.read_unsigned_byten = AbstractStream.read_unsigned_byten[opcode - self.base_opcode]

    ##############################################

    def read_parameters(self, virtual_font_parser):

        stream = virtual_font_parser.stream

        font_id = self.read_unsigned_byten(stream)
        checksum = stream.read_unsigned_byte4()
        scale_factor = stream.read_unsigned_byte4()
        design_size = stream.read_unsigned_byte4()
        name = str(stream.read(stream.read_unsigned_byte1() + stream.read_unsigned_byte1()))

        virtual_font = virtual_font_parser.virtual_font
        # The font scale factor is relative to the design size of the virtual font, thus 2**20 means
        # the font has the same size than the virtual font.
        # Fixme: right?
        scale_factor = int(to_fix_word(scale_factor) * design_size / virtual_font.design_font_size)
        dvi_font = DviFont(font_id, name, checksum, scale_factor, design_size)
        virtual_font.register_font(dvi_font)

####################################################################################################

opcode_definitions = (
    ( [vf_opcodes.SHORT_CHAR_000,
       vf_opcodes.LONG_CHAR], OpcodeParser_char ),
    ( [vf_opcodes.FNT_DEF1,
       vf_opcodes.FNT_DEF4], OpcodeParser_fnt_def ),
    ( vf_opcodes.PRE, 'pre', 'preamble', (), None ),
    ( vf_opcodes.POST, 'post', 'postamble beginning', None, None ),
    )

class VirtualFontParser(object):

    _logger = _module_logger.getChild('VirtualFontParser')

    opcode_parser_set = OpcodeParserSet(opcode_definitions)

    ##############################################

    @staticmethod
    def parse(virtual_font):

        VirtualFontParser(virtual_font)

    ##############################################

    def __init__(self, virtual_font):

        self.virtual_font = virtual_font

        self.stream = FileStream(virtual_font.filename)

        self._process_preambule()
        self._process_file()

    ##############################################

    def _process_preambule(self):

        """ Process the preamble. """

        stream = self.stream

        stream.seek(0)

        if stream.read_unsigned_byte1() != vf_opcodes.PRE:
            raise NameError("Virtual font file don't start by PRE opcode")

        file_id = stream.read_unsigned_byte1()
        if file_id != VF_ID:
            raise NameError("Unknown file ID")

        comment = stream.read(stream.read_unsigned_byte1())
        checksum = stream.read_signed_byte4()
        design_font_size = stream.read_fix_word()

#         string_template = '''
# Preambule
#   - Vf ID        %u
#   - Comment      '%s'
#   - Design size  %.1f pt
#   - Checksum     %u
# '''
#         print string_template % (
#             file_id,
#             comment,
#             design_font_size,
#             checksum,
#             )
       
        
        self.virtual_font._set_preambule_data(file_id, comment, design_font_size, checksum)

    ##############################################

    def _process_file(self):

        """ Process the characters. """
        
        stream = self.stream

        # Fixme: to incorporate pre, check here pre is the first code

        while True:
            byte = stream.read_unsigned_byte1()
            if byte == vf_opcodes.POST:
                break
            else:
                # Fixme: self.opcode_parsers[byte]()
                opcode_parser = self.opcode_parser_set[byte]
                opcode_parser.read_parameters(self) # Fixme: return where

####################################################################################################
#
# End
#
####################################################################################################
