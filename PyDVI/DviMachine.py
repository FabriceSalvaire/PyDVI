####################################################################################################
# 
# PyDVI - A Python Library to Process DVI Stream
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
           'DviColorBlack',
           'DviColorGray',
           'DviColorRGB',
           'DviColorCMYK',
           'DviProgam',
           'DviProgramPage',
           'DviMachine',
           'DviSimplifyMachine',
           ]

####################################################################################################

import fractions
import logging

####################################################################################################

from PyDVI.TeXUnit import *
from PyDVI.Tools.EnumFactory import EnumFactory
from PyDVI.Tools.Interval import Interval2D
from PyDVI.Tools.Logging import print_card

####################################################################################################

logger = logging.getLogger(__name__)

####################################################################################################

#: Defines Paper Orientation
paper_orientation_enum = EnumFactory('PaperOrientation',
                                     ('portrait', 'landscape'))

####################################################################################################

class Opcode(object):

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

    def append(self, char_code):

        """ Append the char code. """

        self.characters.append(char_code)

    ##############################################

    def run(self, dvi_machine, compute_bounding_box=False):

        registers = dvi_machine.registers
        current_font = dvi_machine.current_font
        dvi_font = dvi_machine.current_dvi_font

        bounding_box = None
        for char_code in self.characters:
            tfm_char = current_font.tfm[char_code]
            char_width  = dvi_font.char_scaled_width(tfm_char)
            char_depth  = dvi_font.char_scaled_depth(tfm_char)
            char_height = dvi_font.char_scaled_height(tfm_char)
            
            char_bounding_box = Interval2D([registers.h, registers.h + char_width],
                                           [registers.v - char_height, registers.v + char_depth])

            if compute_bounding_box:
                print 'Char bounding box', char_bounding_box
                if bounding_box is None:
                    bounding_box = char_bounding_box
                else:
                    bounding_box |= char_bounding_box
            else:
                dvi_machine.paint_char(registers.h, registers.v,
                                       char_bounding_box,
                                       current_font,
                                       char_code,
                                       dvi_font.magnification)

            if self.set_char:
                registers.h += char_width

            print '%s char %3u "%s" width %8u h %10u' % (self.opcode_name,
                                                         char_code, chr(char_code),
                                                         char_width, registers.h)
            
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
                                      [registers.v + self.height, registers.v])
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
        registers.w  = self.x
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
        registers.x  = self.x
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
        registers.y  = self.x
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
        registers.z  = self.x
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
        self.design_size = design_size

        self.magnification = fractions.Fraction(scale_factor, design_size)

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

        """ Return the scale width for the :class:`PyDVI.TfmChar` instance. """

        return tfm_char.scaled_width(self.scale_factor)

    ##############################################

    def char_scaled_height(self, tfm_char):

        """ Return the scale height for the :class:`PyDVI.TfmChar` instance. """

        return tfm_char.scaled_height(self.scale_factor)

    ##############################################

    def char_scaled_depth(self, tfm_char):

        """ Return the scale depth for the :class:`PyDVI.TfmChar` instance. """

        return tfm_char.scaled_depth(self.scale_factor)

####################################################################################################

class DviColor(object):
    pass
 
####################################################################################################

class DviColorBlack(DviColor):

    """ This class implements the black colour. """

    ##############################################

    def __str__(self):

        return 'Colour Black'

####################################################################################################

class DviColorGray(DviColor):

    """ This class implements gray colour. """

    ##############################################

    def __init__(self, gray_level):

        self.gray_level = gray_level

    ##############################################

    def __str__(self):

        return 'Colour Gray %.1f' % (self.gray_level)

####################################################################################################

class DviColorRGB(DviColor):

    """ This class implements RGB colour. """

    ##############################################

    def __init__(self, red, green, blue):

        self.red, self.green, self.blue = red, green, blue

    ##############################################

    def __str__(self):

        return 'Colour RGB (%.1f, %.1f, %.1f)' % (self.red, self.green, self.blue)

####################################################################################################

class DviColorCMYK(DviColor):

    """ This class implements CMYK colour. """

    ##############################################

    def __init__(self, cyan, magenta, yellow, dark):

        self.cyan, self.magenta, self.yellow, self.dark = cyan, magenta, yellow, dark

    ##############################################

    def __str__(self):

        return 'Colour CMYK (%.1f, %.1f, %.1f, %.1f)' % (self.cyan, self.magenta, self.yellow, self.dark)

####################################################################################################

class DviProgramPage(list):

    """ This class defines a page. """

    ##############################################

    def __init__(self,
                 page_number,
                 height=0, width=0,
                 paper_orientation=paper_orientation_enum.portrait):

        self.page_number = page_number
        self.set_paper_size(height, width)
        self.paper_orientation = paper_orientation

    ##############################################

    def set_paper_size(self, height, width):

        """ Set the paper size. """

        self.height, self.width = height, width

    ##############################################

    def print_program(self):

        """ Print the program. """

        string_format = \
'''Page Program
 - Paper Size: height = %.3f pt width = %.3f pt
 - Paper Orientation: %s
'''

        message = string_format % (
            self.height, self.width,
            self.paper_orientation,
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

    def get_font(self, i):

        return self.fonts[i]

    ##############################################

    def get_page(self, i):

        return self.pages[i]

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

        self.h, self.v, self.w, self.x, self.y, self.z = h, v, w, x, y, z

    ##############################################

    def __str__(self):
        
        string_format = '''
(h=+%10u sp %+10.2f mm v=+%10u sp %+10.2f mm
 w=+%10u sp %+10.2f mm x=+%10u sp %+10.2f mm
 y=+%10u sp %+10.2f mm z=+%10u sp %+10.2f mm)
'''
        return string_format % (
            self.h, sp2mm(self.h),
            self.v, sp2mm(self.v),
            self.w, sp2mm(self.w),
            self.x, sp2mm(self.x),
            self.y, sp2mm(self.y),
            self.z, sp2mm(self.z),
            )

    ##############################################

    def clone(self):

        """ Clone the set of registers. """

        return DviMachineRegisters(self.h, self.v, self.w, self.x, self.y, self.z)

####################################################################################################

class DviMachine(object):

    """ This class implements a DVI Machine. """
    
    ##############################################

    def __init__(self, font_manager):

        self.font_manager = font_manager

        self.fonts = {}
        self.reset()

    ##############################################

    def reset(self):

        """ Reset the machine. """

        self.current_font_id = None
        self.registers_stack = [DviMachineRegisters()]
        self.colour_stack = [DviColorBlack()]

    ##############################################

    def _get_registers(self):

        """ Return the current register set. """

        return self.registers_stack[-1]

    registers = property(_get_registers, None, None, 'Register set')

    ##############################################

    def push_registers(self):

        """ Push the register set. """

        self.registers_stack.append(self.registers.clone())

    ##############################################

    def pop_registers(self, n=1):

        """ Pop *n* level in the register set stack. """

        del self.registers_stack[n]

    ##############################################

    def push_colour(self, colour):

        """ Push the current colour. """

        self.colour_stack.append(colour)

    ##############################################

    def pop_colour(self, n = 1):

        """ Pop *n* level in the colour stack. """

        del self.registers_stack[-n]

    ##############################################

    def _get_current_font(self):

        """ Return the current font. """

        return self.fonts[self.current_font_id]

    current_font = property(_get_current_font, None, None, 'Current font')

    ##############################################

    def _get_current_dvi_font(self):

        """ Return the current dvi font. """

        return self.dvi_program.get_font(self.current_font_id)

    current_dvi_font = property(_get_current_dvi_font, None, None, 'Current dvi font')

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
            self.fonts[dvi_font.id] = self.font_manager[dvi_font.name]

    ##############################################

    def simplify_dvi_program(self):

        """ Simplify the DVI program. """

        dvi_simplify_machine = DviSimplifyMachine(self.font_manager)
        dvi_simplify_machine.load_dvi_program(self.dvi_program, load_fonts=False)
        dvi_simplify_machine.simplify()

    ##############################################

    def run_page(self, page):

        self.reset()

        opcode_program = self.dvi_program.get_page(page)

        print 'Program Length:', len(opcode_program)

        for opcode in opcode_program:
            print opcode
            opcode.run(self)
            print 'level %u' % (len(self.registers_stack)), self.registers

    ##############################################

    def compute_page_bounding_box(self, page):

        self.reset()

        opcode_program = self.dvi_program.get_page(page)

        bounding_box = None
        for opcode in opcode_program:
            print opcode
            opcode_bounding_box = opcode.run(self, compute_bounding_box=True)
            print 'Register Stack level %u' % (len(self.registers_stack)), self.registers
            if opcode_bounding_box is not None:
                print 'Opcode bounding box', opcode_bounding_box
                if bounding_box is None:
                    bounding_box = opcode_bounding_box
                else:
                    bounding_box |= opcode_bounding_box
                print 'Current page bounding box', bounding_box

        print 'Page bounding box\n ', bounding_box, 'sp'
        (x_min_mm, x_max_mm,
         y_min_mm, y_max_mm) = [sp2mm(x) for x in (bounding_box.x.inf, bounding_box.x.sup,
                                                   bounding_box.y.inf, bounding_box.y.sup)]
        print '  [%.2f, %.2f]*[%.2f, %.2f] mm' % (x_min_mm, x_max_mm, y_min_mm, y_max_mm) 

        return bounding_box

    ##############################################

    def paint_rule(self, x, y, width, height):

        pass

    ##############################################

    def paint_char(self, x, y, char_bounding_box, font, char_code, magnification): #!# , glyph

        pass

####################################################################################################

class DviSimplifyMachine(DviMachine):

    #: Defines papersize special
    xxx_papersize = 'papersize='

    #: Defines landscape special
    xxx_landscape = '! /landplus90 true store'

    #: Defines colour special
    xxx_colour = 'color '
    
    ##############################################

    def simplify(self):

        """ Simplify the program. """

        logger.info('Process the xxx opcodes in the program')

        for program_page in self.dvi_program:
            self.simplify_page(program_page)
            self.process_page_xxx_opcodes(program_page)

    ##############################################

    def process_page_xxx_opcodes(self, program_page):

        """ Process the xxx opcodes in the page program. """

        logger.info('Process the xxx opcodes in the page program #%u' % program_page.page_number)

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

    ##############################################

    def transform_xxx_colour(self, program_page, xxx_code):

        """ Transform a xxx colour opcode. """

        logger.info("Transform the xxx colour opcode: '%s'" % xxx_code)

        words = xxx_code.split()

        try:
            operation = words[1]
            if operation == 'pop':
                return Opcode_pop_colour()

            elif operation == 'push':
                colour_class = words[2]
                if colour_class == 'Black':
                    colour = DviColorBlack()
                elif colour_class == 'gray':
                    colour = DviColorGray(float(words[3]))
                elif colour_class == 'rgb':
                    colour = DviColorRGB(* [float(x) for x in words[3:6]])
                elif colour_class == 'cmyk':
                    colour = DviColorCMYK(* [float(x) for x in words[3:7]])
                else:
                    raise ValueError('Unknown colour type')
                return Opcode_push_colour(colour)

        except:
            # Fixme: ValueError
            return None

    ##############################################

    def transform_xxx_paper_size(self, program_page, xxx_code):

        """ Transform a xxx paper size opcode. """

        logger.info("Transform the xxx paper size opcode: '%s'" % xxx_code)

        start = xxx_code.rfind('=') +1
        dimensions = xxx_code[start:]
        height, width = [float(x[:-2]) for x in dimensions.split(',')]

        program_page.set_paper_size(height, width)

        return None

    ##############################################

    def transform_xxx_paper_orientation(self, program_page, xxx_code):

        """ Transform a xxx paper orientation opcode. """

        logger.info("Transform the paper orientation opcode: '%s'" % xxx_code)

        if xxx_code == self.xxx_landscape:
            program_page.set_paper_orientation = paper_orientation_enum.landscape
 
        return None

    ##############################################

    def simplify_page(self, program_page):

        """ Simplify the page. """

        logger.info('Simplify the program page #%u' % program_page.page_number)

        i = 0
        previous_opcode = None
        while i < len(program_page):
            opcode = program_page[i]
            delete_opcode = False

            if previous_opcode is not None and opcode.__class__ == previous_opcode.__class__:
                logger.info("Same opcode %s" % opcode.__class__.__name__)

                if isinstance(opcode, (Opcode_pop, Opcode_pop_colour)):
                    logger.info("Merge pop opcode")
                    previous_opcode.n += 1
                    delete_opcode = True

                elif isinstance(opcode, OpcodeX):
                    logger.info("Merge OpcodeX")
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

####################################################################################################
#
# End
#
####################################################################################################
