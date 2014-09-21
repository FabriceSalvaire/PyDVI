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

####################################################################################################
#
# Audit
#
# - 17/12/2011 fabrice
#   - __init__
#
####################################################################################################

####################################################################################################

__all__ = ['Opcode_set_char',
           'Opcode_put_char',
           'Opcode_set_rule',
           'Opcode_put_rule',
           'Opcode_push',
           'Opcode_pop',
           'Opcode_push_colour',
           'Opcode_pop_colour',
           'Opcode_right',
           'Opcode_w0',
           'Opcode_w',
           'Opcode_x0',
           'Opcode_x',
           'Opcode_down',
           'Opcode_y0',
           'Opcode_y',
           'Opcode_z0',
           'Opcode_z',
           'Opcode_font',
           'Opcode_xxx',
           'DviFont',
           'DviColourBlack',
           'DviColourGray',
           'DviColourRGB',
           'DviColourCMYK',
           'DviProgam',
           'DviProgramPage',
           'DviSubroutine',
           'DviMachine',
           'DviSimplifyMachine',
           ]

####################################################################################################

import fractions
import logging

####################################################################################################

from ..TeXUnit import *
from ..Tools.EnumFactory import EnumFactory
from ..Tools.Interval import Interval2D

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

#: Defines Paper Orientation
paper_orientation_enum = EnumFactory('PaperOrientation',
                                     ('portrait', 'landscape'))

####################################################################################################

class Opcode(object):

    _logger = _module_logger.getChild('Opcode')

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        pass

####################################################################################################

class OpcodeX(Opcode):

    ##############################################

    def __init__(self, x):

        self.x = x

####################################################################################################

class Opcode_putset_char(Opcode):

    """ This class implements the ``set_char`` and ''put_char`` opcodes. """

    ##############################################

    def __init__(self, char_code, set_char=True):

        self.characters = [char_code]
        self.set_char = set_char

    ##############################################

    def __str__(self):

        return '%s char "%s"' % (self.opcode_name,
                                 ''.join([chr(x) for x in self.characters]))

    ##############################################

    def __len__(self):

        return len(self.characters)

    ##############################################

    def append(self, char_code):

        """ Append the char code. """

        self.characters.append(char_code)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        font = dvi_machine.current_font
        dvi_font = dvi_machine.current_dvi_font
        if font.is_virtual:
            # Fixme: bounding_box
            for char_code in self.characters:
                virtual_character = font._characters[char_code]
                dvi_machine.run_subroutine(virtual_character.subroutine)
                tfm_char = font.tfm[char_code]
                char_width = dvi_font.char_scaled_width(tfm_char)
                registers.h += char_width # Fixme: properly scaled
        else:
            self._run(dvi_machine, compute_bounding_box)

    ##############################################

    def _run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        font = dvi_machine.current_font
        dvi_font = dvi_machine.current_dvi_font

        bounding_box = None
        for char_code in self.characters:
            if font.tfm is not None:
                tfm_char = font.tfm[char_code]
                char_width = dvi_font.char_scaled_width(tfm_char)
                char_depth = dvi_font.char_scaled_depth(tfm_char)
                char_height = dvi_font.char_scaled_height(tfm_char)
            else: # Fixme:
                size = dvi_font.magnification * sp2pt(dvi_font.design_size)
                glyph = font.get_glyph(char_code, size)
                print glyph.advance, glyph.size, glyph.width_px
                char_width = glyph.px_to_mm(glyph.width_px)
                char_depth = glyph.px_to_mm(glyph.height_px - glyph.horizontal_bearing_y_px)
                char_height = glyph.px_to_mm(glyph.horizontal_bearing_y_px)

            char_bounding_box = Interval2D([registers.h, registers.h + char_width],
                                           [registers.v - char_height, registers.v + char_depth])

            if compute_bounding_box:
                # self._logger.info('Char bounding box\n{}'.format(char_bounding_box))
                if bounding_box is None:
                    bounding_box = char_bounding_box
                else:
                    bounding_box |= char_bounding_box
            else:
                dvi_machine.paint_char(registers.h, registers.v,
                                       char_bounding_box,
                                       font,
                                       dvi_font,
                                       char_code)

            if self.set_char:
                registers.h += char_width

            # self._logger.info('{} char {:3} "{}" width {:8} h {:10}'.format(self.opcode_name,
            #                                                                 char_code, chr(char_code),
            #                                                                 char_width, registers.h))
            
        if compute_bounding_box:
            return bounding_box

####################################################################################################

class Opcode_set_char(Opcode_putset_char):

    """ This class implements the ``set_char`` opcode. """

    ##############################################

    def __init__(self, char_code):

        super(Opcode_set_char, self).__init__(char_code, set_char=True)

        self.opcode_name = 'set'

####################################################################################################

class Opcode_put_char(Opcode_putset_char):

    """ This class implements the ``put_char`` opcode. """

    ##############################################

    def __init__(self, char_code):

        super(Opcode_put_char, self).__init__(char_code, set_char=False)

        self.opcode_name = 'put'

####################################################################################################

class Opcode_putset_rule(Opcode):

    """ This class implements the ``set_rule`` and ``put_rule`` opcodes. """

    ##############################################

    def __init__(self, height, width, set_rule=True):

        self.height = height
        self.width = width
        self.set_rule = set_rule

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers

        if compute_bounding_box:
            # Fixme: check
            bounding_box = Interval2D([registers.h, registers.h + self.width],
                                      [registers.v, registers.v + self.height])
        else:
            dvi_machine.paint_rule(registers.h, registers.v, self.width, self.height)

        if self.set_rule:
            registers.h += self.width

        if compute_bounding_box:
            return bounding_box

####################################################################################################

class Opcode_set_rule(Opcode_putset_rule):

    """ This class implements the ``set_rule`` opcode. """

    ##############################################

    def __init__(self, height, width):

        super(Opcode_set_rule, self).__init__(height, width, set_rule=False)

    ##############################################

    def __str__(self):

        return 'set rule height %u width %u, h += width' % (self.height, self.width)

####################################################################################################

class Opcode_put_rule(Opcode_putset_rule):

    """ This class implements the ``put_rule`` opcode. """

    ##############################################

    def __init__(self, height, width):

        super(Opcode_put_rule, self).__init__(height, width, set_rule=False)

    ##############################################

    def __str__(self):
        
        return 'put rule height %u width %u' % (self.height, self.width)

####################################################################################################

class Opcode_push(Opcode):

    """ This class implements the ``push`` opcode. """

    ##############################################

    def __str__(self):

        return 'push register'

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        dvi_machine.push_registers()

####################################################################################################

class Opcode_pop(Opcode):

    """ This class implements the ``pop`` opcode. """

    ##############################################

    def __init__(self, n=1):

        self.n = n

    ##############################################

    def __str__(self):

        return 'pop register *%u' % (self.n)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        dvi_machine.pop_registers(self.n)

####################################################################################################

class Opcode_push_colour(Opcode):

    """ This class implements the ``push_colour`` opcode. """

    ##############################################

    def __init__(self, colour):

        self.colour = colour

    ##############################################

    def __str__(self):

        return 'push colour' + str(self.colour)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        dvi_machine.push_colour(self.colour)

####################################################################################################

class Opcode_pop_colour(Opcode):

    """ This class implements the ``pop_colour`` opcode. """

    ##############################################

    def __init__(self, n = 1):

        self.n = n

    ##############################################

    def __str__(self):

        return 'pop colour *%u' % (self.n)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        dvi_machine.pop_colour(self.n)

####################################################################################################

class Opcode_right(OpcodeX):

    """ This class implements the ``right`` opcode. """

    ##############################################

    def __str__(self):

        # Fixme: -> function

        return 'h += %+u sp %+.2f mm' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.h += self.x

####################################################################################################

class Opcode_w0(Opcode):

    """ This class implements the ``w0`` opcode. """

    ##############################################

    def __str__(self):

        return 'h += w'

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.h += registers.w

####################################################################################################

class Opcode_w(OpcodeX):

    """ This class implements the ``w`` opcode. """

    ##############################################

    def __str__(self):

        return 'w = %+u sp %+.2f mm, h += w' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.w = self.x
        registers.h += self.x

####################################################################################################

class Opcode_x0(Opcode):

    """ This class implements the ``x0`` opcode. """

    ##############################################

    def __str__(self):

        return 'h += x'

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.h += registers.x

####################################################################################################

class Opcode_x(OpcodeX):

    """ This class implements the ``x`` opcode. """

    ##############################################

    def __str__(self):

        return 'x = %+u sp %+.2f mm, h += x' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.x = self.x
        registers.h += self.x

####################################################################################################

class Opcode_down(OpcodeX):

    """ This class implements the ``down`` opcode. """

    ##############################################

    def __str__(self):

        return 'v += %+u sp %+.2f mm' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.v += self.x

####################################################################################################

class Opcode_y0(Opcode):

    """ This class implements the ``y0`` opcode. """

    ##############################################

    def __str__(self):

        return 'v += y'

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.v += registers.y

####################################################################################################
 
class Opcode_y(OpcodeX):

    """ This class implements the ``y`` opcode. """

    ##############################################

    def __str__(self):

        return 'y = %+u sp %+.2f mm, v += y' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.y = self.x
        registers.v += self.x

####################################################################################################

class Opcode_z0(Opcode):

    """ This class implements the ``z0`` opcode. """

    ##############################################

    def __str__(self):

        return 'v += z'

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.v += registers.z

####################################################################################################

class Opcode_z(OpcodeX):

    """ This class implements the ``z`` opcode. """

    ##############################################

    def __str__(self):

        return 'z = %+u sp %+.2f mm, v += z' % (self.x, sp2mm(self.x))

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        registers.z = self.x
        registers.v += self.x

####################################################################################################

class Opcode_font(Opcode):

    """ This class implements the ``font`` opcode. """

    ##############################################

    def __init__(self, font_id):

        self.font_id = font_id

    ##############################################

    def __str__(self):

        return 'font %u' % (self.font_id)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        dvi_machine.current_font_id = self.font_id

####################################################################################################

class Opcode_xxx(Opcode):

    """ This class implements the ``xxx`` opcode. """

    ##############################################

    def __init__(self, code):

        self.code = code

    ##############################################

    def __str__(self):

        return 'xxx [%s]' % (self.code)

####################################################################################################

class DviFont(object):

    """ This class implements a DVI Font. """

    ##############################################

    def __init__(self, font_id, name, checksum, scale_factor, design_size):

        self.id = font_id
        self.name = name
        self.checksum = checksum
        self.scale_factor = scale_factor
        self.design_size = design_size # pt

        self.magnification = fractions.Fraction(scale_factor, design_size)

        self.global_id = None

    ##############################################

    def __repr__(self):

        return 'Dvi Font[{}] {}'.format(self.id, self.name)

    ##############################################

    def __str__(self):

        string_format = '''Font ID %u
 - Name          %s
 - Checksum      %u
 - Design size   %u
 - Scale factor  %u
 - Magnification %u %%
'''
        
        return string_format % (
            self.id,
            self.name,
            self.checksum,
            self.scale_factor,
            self.design_size,
            self.magnification * 100,
            )

    ##############################################

    def char_scaled_width(self, tfm_char):

        """ Return the scale width for the :class:`PyDvi.TfmChar` instance. """

        return tfm_char.scaled_width(self.scale_factor)

    ##############################################

    def char_scaled_height(self, tfm_char):

        """ Return the scale height for the :class:`PyDvi.TfmChar` instance. """

        return tfm_char.scaled_height(self.scale_factor)

    ##############################################

    def char_scaled_depth(self, tfm_char):

        """ Return the scale depth for the :class:`PyDvi.TfmChar` instance. """

        return tfm_char.scaled_depth(self.scale_factor)

####################################################################################################

class DviColour(object):

    ##############################################

    def __init__(self, red, green, blue, alpha=1):

        # alpha = 1 means fully opaque

        self.red, self.green, self.blue = red, green, blue
        self.alpha = alpha

    ##############################################

    @property
    def colour(self):
        return self.red, self.green, self.blue, self.alpha
 
####################################################################################################

class DviColourBlack(DviColour):

    """ This class implements the black colour. """

    ##############################################

    def __init__(self):

        super(DviColourBlack, self).__init__(0, 0, 0)

    ##############################################

    def __str__(self):

        return 'Colour Black'

####################################################################################################

class DviColourGray(DviColour):

    """ This class implements gray colour. """

    ##############################################

    def __init__(self, gray_level):

        self.gray_level = gray_level

        super(DviColourGray, self).__init__(gray_level, gray_level, gray_level)

    ##############################################

    def __str__(self):

        return 'Colour Gray %.1f' % (self.gray_level)

####################################################################################################

class DviColourRGB(DviColour):

    """ This class implements RGB colour. """

    ##############################################

    def __str__(self):

        return 'Colour RGB (%.1f, %.1f, %.1f)' % (self.red, self.green, self.blue)

####################################################################################################

class DviColourCMYK(DviColour):

    """ This class implements CMYK colour. """

    ##############################################

    def __init__(self, cyan, magenta, yellow, dark):

        # We don't use an ICC profile to perform the conversion
        luminosity = 1 - dark
        red = (1 - cyan) * luminosity
        green = (1 - magenta) * luminosity
        blue = (1 - yellow) * luminosity

        super(DviColourCMYK, self).__init__(red, green, blue)

        self.cyan, self.magenta, self.yellow, self.dark = cyan, magenta, yellow, dark

    ##############################################

    def __str__(self):

        template = 'Colour CMYK (%.1f, %.1f, %.1f, %.1f) RGB (%.1f, %.1f, %.1f)'
        return  template % (self.cyan, self.magenta, self.yellow, self.dark,
                            self.red, self.green, self.blue)

####################################################################################################

class DviSubroutine(list):

    ##############################################

    def __init__(self):

        super(DviSubroutine, self).__init__()

        self.number_of_rules = None
        self.number_of_chars = None

####################################################################################################

class DviProgramPage(list):

    """ This class defines a page. """

    ##############################################

    def __init__(self,
                 page_number,
                 height=0, width=0,
                 paper_orientation=paper_orientation_enum.portrait):

        super(DviProgramPage, self).__init__()

        self.page_number = page_number
        self.set_paper_size(height, width)
        self.paper_orientation = paper_orientation

        self.number_of_rules = None
        self.number_of_chars = None

        self.is_opcodes_simplified = False
        self.is_xxx_opcodes_simplified = False

    ##############################################

    def set_paper_size(self, height, width):

        """ Set the paper size in mm. """

        self.height, self.width = height, width

    ##############################################

    def print_program(self):

        """ Print the program. """

        string_format = \
'''Page Program
 - Paper Size: height = {:.3f} pt width = {:.3f} pt
 - Paper Orientation: {}
 - number of rules: {}
 - number of characters: {}
'''

        message = string_format.format(self.height, self.width,
                                       self.paper_orientation,
                                       self.number_of_rules,
                                       self.number_of_chars,
                                      )
        
        print message
        for opcode in self:
            print opcode

####################################################################################################

class DviProgam(object):

    """ This class implements a DVI program. """

    ##############################################

    def __init__(self):

        self.fonts = {} # dict of DviFont
        self.pages = []

        # Fixme: default parameters
        self.max_height, self.max_width = 0, 0
        self.stack_depth = 0
        self.number_of_pages = 0

    ##############################################

    def __getitem__(self, i):

        # Fixme: for long document, the dvi stream should be read on demand: lazy loading
        return self.pages[i]

    ##############################################

    def __iter__(self):

        for opcode_program in self.pages:
            yield opcode_program

    ##############################################

    def __len__(self):

        return len(self.pages)

    ##############################################

    def dvi_font_iterator(self):
        
        return self.fonts.itervalues()

    ##############################################

    def set_preambule_data(self,
                           comment,
                           dvi_format,
                           numerator, denominator, magnification):

        """ Set the preambule data. """

        self.comment = comment
        self.dvi_format = dvi_format
        self.numerator, self.denominator, self.magnification = numerator, denominator, magnification

        # Fixme: use it to convert
        self.dvi_unit = fractions.Fraction(self.magnification * self.numerator,
                                           1000 * self.denominator) # 1e-7 m

    ##############################################

    def set_postambule_data(self,
                            max_height, max_width,
                            stack_depth,
                            number_of_pages):

        """ Set the postamble data. """

        self.max_height, self.max_width = max_height, max_width
        self.stack_depth = stack_depth
        self.number_of_pages = number_of_pages

        for i in xrange(self.number_of_pages):
            self.pages.append(DviProgramPage(i))

    ##############################################

    def append_page(self, i):

        self.pages.append(DviProgramPage(i))

    ##############################################
        
    def register_font(self, font):

        """ Register a :class:`DviFont` instance. """

        if font.id not in self.fonts:
            self.fonts[font.id] = font
        # else:
        #     print 'Font ID %u already registered' % (font.id)
            
    ##############################################

    # Fixme: property ?
    def get_font(self, i):

        return self.fonts[i]

    ##############################################

    def print_summary(self):

        string_format = '''DVI Program

Preambule
  - Comment       '%s'
  - DVI format    %u
  - Numerator     %u
  - Denominator   %u
  - Magnification %u
  - DVI unit      %.1f nm

Postamble
  - Number of Pages %u
  - Stack Depth     %u
  - Max Height      %u sp %.1f mm
  - Max Width       %u sp %.1f mm
'''

        print string_format  % (
            self.comment,
            self.dvi_format,
            self.numerator,
            self.denominator,
            self.magnification,
            self.dvi_unit * 100,
            self.number_of_pages,
            self.stack_depth,
            self.max_height, sp2mm(self.max_height),
            self.max_width, sp2mm(self.max_width),
       )
        
        print 'List of fonts:'
        for font in self.dvi_font_iterator():
            print font

        # for i in xrange(self.number_of_pages):
        #     print '\nPage', i
        #     self.pages[i].print_program()

####################################################################################################

one_in_sp = in2sp(1)

class DviMachineRegisters(object):

    """ This class implements a set of registers. """

    ##############################################

    def __init__(self, h=one_in_sp, v=one_in_sp, w=0, x=0, y=0, z=0):

        self.h, self.v = h, v # horizontal and vertical position
        self.w, self.x, self.y, self.z = w, x, y, z

    ##############################################

    def __str__(self):
        
        string_format = '''
(h=+%10u sp %+10.2f mm v=+%10u sp %+10.2f mm
 w=+%10u sp %+10.2f mm x=+%10u sp %+10.2f mm
 y=+%10u sp %+10.2f mm z=+%10u sp %+10.2f mm)
'''
        return string_format.strip() % (
            self.h, sp2mm(self.h),
            self.v, sp2mm(self.v),
            self.w, sp2mm(self.w),
            self.x, sp2mm(self.x),
            self.y, sp2mm(self.y),
            self.z, sp2mm(self.z),
            )

    ##############################################

    def clone(self, reset=False):

        """ Clone the set of registers. """

        if reset:
            return DviMachineRegisters(self.h, self.v, 0, 0, 0, 0)
        else:
            return DviMachineRegisters(self.h, self.v, self.w, self.x, self.y, self.z)

####################################################################################################

class DviMachine(object):

    """ This class implements a DVI Machine. """

    _logger = _module_logger.getChild('DviMachine')
    
    ##############################################

    def __init__(self, font_manager):

        self.font_manager = font_manager

        self.virtual_fonts = {}
        self.fonts = {} # indexed by TeX font id which is not an incremental number starting from 0
        self._reset()

    ##############################################

    def _reset(self):

        """ Reset the machine. """

        self.current_opcode_program = None
        self._current_font_id = None
        self._virtual_font = None
        self.in_subroutine = False
        self._registers_stack = [DviMachineRegisters()]
        self._colour_stack = [DviColourBlack()]

    ##############################################

    @property
    def registers(self):
        """ Return the current register set. """
        return self._registers_stack[-1]

    ##############################################

    def push_registers(self, reset=False):
        """ Push the register set. """
        self._registers_stack.append(self.registers.clone(reset))

    ##############################################

    def pop_registers(self, n=1):
        """ Pop *n* level in the register set stack. """
        for i in xrange(n):
            del self._registers_stack[-1]

    ##############################################

    @property
    def current_colour(self):
        """ Return the current colour. """
        return self._colour_stack[-1]

    ##############################################

    def push_colour(self, colour):
        """ Push the current colour. """
        self._colour_stack.append(colour)

    ##############################################

    def pop_colour(self, n=1):
        """ Pop *n* level in the colour stack. """
        for i in xrange(n):
            del self._colour_stack[-1]

    ##############################################

    @property
    def current_font_id(self):
        return self._current_font_id

    ##############################################

    @current_font_id.setter
    def current_font_id(self, font_id):
        if self._virtual_font is not None:
            font_id = self._virtual_font.font_id_map[font_id]
        self._current_font_id = font_id

    ##############################################

    @property
    def current_font(self):
        """ Return the current font. """
        return self.fonts[self._current_font_id]

    ##############################################

    @property
    def is_current_font_virtual(self):
        return self.current_font.is_virtual

    ##############################################

    @property
    def current_dvi_font(self):
        """ Return the current dvi font. """
        return self.dvi_program.get_font(self._current_font_id)

    ##############################################

    def load_dvi_program(self, dvi_program, load_fonts=True):

        """ Load a :class:`DviProgam` instance. """

        self.dvi_program = dvi_program
        if load_fonts:
            self._load_dvi_fonts()

    ##############################################

    def _load_dvi_fonts(self):

        """ Load the fonts used by the DVI program. """

        # Load the Fonts
        for dvi_font in self.dvi_program.dvi_font_iterator():
            font = self.font_manager[dvi_font.name]
            self.fonts[dvi_font.id] = font
            if font.is_virtual:
                self.virtual_fonts[dvi_font.id] = font
                font.load_dvi_fonts()

        # Merge the embedded fonts in the virtual fonts
        last_font_id = max([font_id for font_id in self.fonts])
        for virtual_font in self.virtual_fonts.itervalues():
            for font in virtual_font.fonts.itervalues():
                last_font_id += 1
                font.global_id = last_font_id
                self.fonts[last_font_id] = font
            virtual_font.update_font_id_map()
            for font_id, dvi_font in virtual_font.dvi_fonts.iteritems():
                global_font_id = virtual_font.font_id_map[font_id]
                dvi_font.global_id = global_font_id
                self.dvi_program.fonts[global_font_id] = dvi_font
                
        if self.virtual_fonts:
            # Fixme: program_page vs opcode_program
            for program_page in self.dvi_program:
                self._adjust_opcode_counts_for_virtual_characters(program_page)
                # self._merge_virtual_font(program_page)

    ##############################################

    # def _merge_virtual_font(self, opcode_program):

    #     self._reset()
    #     current_font_id = None
    #     for opcode in opcode_program:
    #         if isinstance(opcode, Opcode_font):
    #             opcode.run(self)
    #             current_font_id = self._current_font_id
    #         elif (isinstance(opcode, Opcode_putset_char) and
    #               current_font_id in self.virtual_fonts):
    #             print 'virtual character'

    ##############################################

    def simplify_dvi_program(self):

        """ Simplify the DVI program. """

        dvi_simplify_machine = DviSimplifyMachine(self.font_manager)
        dvi_simplify_machine.load_dvi_program(self.dvi_program, load_fonts=False)
        dvi_simplify_machine.simplify()

    ##############################################

    def count_opcodes(self, opcode_program):

        self._reset()
        number_of_rules = 0
        number_of_chars = {font_id:0 for font_id in self.fonts}
        current_font_id = None
        for opcode in opcode_program:
            if isinstance(opcode, Opcode_font):
                opcode.run(self)
                current_font_id = self._current_font_id
            elif isinstance(opcode, Opcode_putset_rule):
                number_of_rules += 1
            elif isinstance(opcode, Opcode_putset_char):
                number_of_chars[current_font_id] += len(opcode)

        return number_of_rules, number_of_chars

    ##############################################

    def _adjust_opcode_counts_for_virtual_characters(self, opcode_program):

        self._reset()
        current_font_id = None
        is_virtual = False
        for opcode in opcode_program:
            if isinstance(opcode, Opcode_font):
                opcode.run(self)
                current_font_id = self._current_font_id
                is_virtual = self.is_current_font_virtual
            elif isinstance(opcode, Opcode_putset_char) and is_virtual:
                virtual_font = self.current_font
                opcode_program.number_of_chars[current_font_id] -= 1
                self._adjust_opcode_counts(opcode_program, virtual_font, opcode.characters)

    ##############################################

    def _adjust_opcode_counts(self, opcode_program, virtual_font, characters):

        for char_code in characters:
            subroutine = virtual_font[char_code].subroutine
            opcode_program.number_of_rules += subroutine.number_of_rules
            for local_font_id, count in subroutine.number_of_chars.iteritems():
                if local_font_id is None:
                    local_font_id = virtual_font.first_font
                global_font_id = virtual_font.font_id_map[local_font_id]
                if global_font_id in opcode_program.number_of_chars:
                    opcode_program.number_of_chars[global_font_id] += count
                else:
                    opcode_program.number_of_chars[global_font_id] = count

    ##############################################

    def run_page(self, page_index, **kwargs):

        self._reset()
        self.current_opcode_program = self.dvi_program[page_index]
        # self._logger.info('Program Length: {}'.format(len(self.current_opcode_program)))
        self.begin_run_page(**kwargs)
        for opcode in self.current_opcode_program:
            # self._logger.info(opcode)
            opcode.run(self)
            # self._logger.info('Registers:\n'
            #                   'level {}\n'
            #                   '{}'.format(len(self._registers_stack), self.registers))
        self.end_run_page()

    ##############################################

    def begin_run_page(self):
        pass

    def end_run_page(self):
        pass

    ##############################################

    def run_subroutine(self, subroutine):

        self.in_subroutine = True
        self._virtual_font = self.current_font
        current_font_id = self._current_font_id # the virtual font
        self._current_font_id = self._virtual_font.font_id_map[self._virtual_font.first_font]
        self.push_registers(reset=True) # colour ?

        # Fixme: dimension are 2**-20 * virtual font design size
        for opcode in subroutine:
            self._logger.info(opcode)
            opcode.run(self)
            # self._logger.info('Registers:\n'
            #                   'level {}\n'
            #                   '{}'.format(len(self._registers_stack), self.registers))

        self.pop_registers()
        self._current_font_id = current_font_id
        self._virtual_font = None
        self.in_subroutine = False

    ##############################################

    def compute_page_bounding_box(self, page_index):

        self._reset()

        opcode_program = self.dvi_program[page_index]

        bounding_box = None
        for opcode in opcode_program:
            self._logger.info(str(opcode))
            opcode_bounding_box = opcode.run(self, compute_bounding_box=True)
            # self._logger.info('Register Stack level {}\n{}'.format(len(self._registers_stack), self.registers))
            if opcode_bounding_box is not None:
                # self._logger.info('Opcode bounding box {}'.format(opcode_bounding_box))
                if bounding_box is None:
                    bounding_box = opcode_bounding_box
                else:
                    bounding_box |= opcode_bounding_box
                # self._logger.info('Current page bounding box {}'.format(bounding_box))

        (x_min_mm, x_max_mm,
         y_min_mm, y_max_mm) = [sp2mm(x) for x in (bounding_box.x.inf, bounding_box.x.sup,
                                                   bounding_box.y.inf, bounding_box.y.sup)]
        # self._logger.info('Page bounding box\n {} sp\n'
        #                   '  [{:.2f}, {:.2f}]*[{:.2f}, {:.2f}] mm'.format(bounding_box,
        #                                                                   x_min_mm, x_max_mm,
        #                                                                   y_min_mm, y_max_mm) )

        return bounding_box

    ##############################################

    def paint_rule(self, x, y, width, height):

        pass

    ##############################################

    def paint_char(self, x, y, char_bounding_box, font, dvi_font, char_code): #!# , glyph

        pass

####################################################################################################

class DviSimplifyMachine(DviMachine):

    # Fixme:
    #  - merge push

    #: Defines papersize special
    xxx_papersize = 'papersize='

    #: Defines landscape special
    xxx_landscape = '! /landplus90 true store'

    #: Defines colour special
    xxx_colour = 'color '
    
    ##############################################

    def simplify(self, simplify_opcodes=False):

        """ Simplify the program. """

        _module_logger.info('Process the xxx opcodes in the program')
        for program_page in self.dvi_program:
            if simplify_opcodes:
                self.simplify_page(program_page)
            self.process_page_xxx_opcodes(program_page)

    ##############################################

    def process_page_xxx_opcodes(self, program_page):

        """ Process the xxx opcodes in the page program. """

        if program_page.is_xxx_opcodes_simplified:
            return

        _module_logger.info('Process the xxx opcodes in the page program #%u' % program_page.page_number)

        i = 0
        while i < len(program_page):
            opcode = program_page[i]
            if isinstance(opcode, Opcode_xxx):
                xxx_code = opcode.code
                if xxx_code.startswith(self.xxx_papersize):
                    new_opcode = self.transform_xxx_paper_size(program_page, xxx_code)
                elif xxx_code == self.xxx_landscape:
                    new_opcode = self.transform_xxx_paper_orientation(program_page, xxx_code)
                elif xxx_code.startswith(self.xxx_colour):
                    new_opcode = self.transform_xxx_colour(program_page, xxx_code)
                else:
                    new_opcode = None

                if new_opcode is not None:
                    program_page[i] = new_opcode
                    i += 1
                else:
                    del program_page[i]

            else:
                i += 1

        program_page.is_xxx_opcodes_simplified = True

    ##############################################

    def transform_xxx_colour(self, program_page, xxx_code):

        """ Transform a xxx colour opcode. """

        _module_logger.info("Transform the xxx colour opcode: '%s'" % xxx_code)

        # color pop
        # color push  Black
        # color push rgb 1 0 0
        # color push gray .5
        # color push cmyk .1 .8 .5 .0
        words = xxx_code.split()
        try:
            operation = words[1]
            if operation == 'pop':
                return Opcode_pop_colour()

            elif operation == 'push':
                colour_class = words[2]
                if colour_class == 'Black':
                    colour = DviColourBlack()
                elif colour_class == 'gray':
                    colour = DviColourGray(float(words[3]))
                elif colour_class == 'rgb':
                    colour = DviColourRGB(* [float(x) for x in words[3:6]])
                elif colour_class == 'cmyk':
                    colour = DviColourCMYK(* [float(x) for x in words[3:7]])
                else:
                    raise ValueError('Unknown colour type')
                return Opcode_push_colour(colour)

        except:
            # Fixme: ValueError
            return None

    ##############################################

    def transform_xxx_paper_size(self, program_page, xxx_code):

        """ Transform a xxx paper size opcode. """

        _module_logger.info("Transform the xxx paper size opcode: '%s'" % xxx_code)

        # papersize=597.50787pt,845.04684pt
        start = xxx_code.rfind('=') +1
        dimensions = xxx_code[start:]
        width, height = [pt2mm(float(x[:-2])) for x in dimensions.split(',')]

        program_page.set_paper_size(height, width)

        return None

    ##############################################

    def transform_xxx_paper_orientation(self, program_page, xxx_code):

        """ Transform a xxx paper orientation opcode. """

        _module_logger.info("Transform the paper orientation opcode: '%s'" % xxx_code)

        # ! /landplus90 true store
        if xxx_code == self.xxx_landscape:
            program_page.set_paper_orientation = paper_orientation_enum.landscape
 
        return None

    ##############################################

    def simplify_page(self, program_page):

        """ Simplify the page. """

        if program_page.is_opcodes_simplified:
            return

        _module_logger.info('Simplify the program page #%u' % program_page.page_number)

        i = 0
        previous_opcode = None
        while i < len(program_page):
            opcode = program_page[i]
            delete_opcode = False

            if previous_opcode is not None and opcode.__class__ == previous_opcode.__class__:
                _module_logger.info("Same opcode %s" % opcode.__class__.__name__)

                if isinstance(opcode, (Opcode_pop, Opcode_pop_colour)):
                    _module_logger.info("Merge pop opcode")
                    previous_opcode.n += 1
                    delete_opcode = True

                elif isinstance(opcode, OpcodeX):
                    _module_logger.info("Merge OpcodeX {}".format(opcode))
                    previous_opcode.x += opcode.x
                    delete_opcode = True
                    if previous_opcode.x == 0:
                        # delete also previous opcode
                        del program_page[i-1]
                        i -= 1

            if delete_opcode:
                del program_page[i]
            else:
                previous_opcode = opcode
                i += 1

        program_page.is_opcodes_simplified = True

####################################################################################################
#
# End
#
####################################################################################################
