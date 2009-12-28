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
#   - __init__
#
#####################################################################################################

#####################################################################################################

import fractions
import string

#####################################################################################################

from FontManager import *
from TeXUnit import *
from Interval import *

#####################################################################################################

class OpcodeProgram(object):

    ###############################################

    def __init__(self):

        self.program = []

    ###############################################

    def __iter__(self):

        for opcode in self.program:
            yield opcode

    ###############################################

    def __len__(self):

        return len(self.program)

    ###############################################

    def append(self, opcode):

        self.program.append(opcode)

    ###############################################

    def print_program(self):

        for opcode in self.program:
            print opcode

#####################################################################################################

class Opcode(object):

    ###############################################

    def __init__(self):

        pass

#####################################################################################################

class Opcode_set_char(Opcode):

    ###############################################

    def __init__(self, char, set = True):

        self.characters = [char]

        self.set = set

        if self.set is True:
            self.opcode_name = 'set'
        else:
            self.opcode_name = 'put'

    ###############################################

    def __str__(self):

        return '%s char "%s"' % (self.opcode_name, string.join(map(chr, self.characters), sep = ''))

        # return 'set char "%s"' % str(self.characters)

    ###############################################

    def append(self, char):

        self.characters.append(char)

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()

        current_font = dvi_machine.get_current_font()
        dvi_font = dvi_machine.get_current_dvi_font()

        bounding_box = None

        for char_code in self.characters:

            tfm_char = current_font.tfm[char_code]

            glyph = current_font[char_code]
            
            # glyph.print_summary()
            # glyph.print_glyph()
               
            char_width  = dvi_font.get_char_scaled_width(tfm_char)
            char_depth  = dvi_font.get_char_scaled_depth(tfm_char)
            char_height = dvi_font.get_char_scaled_height(tfm_char)
            
            char_bounding_box = Interval2D([registers.h, registers.h + char_width],
                                           [registers.v + char_depth, registers.v - char_height])

            # registers.h - glyph.horizontal_offset,
            # registers.v - glyph.vertical_offset,

            if compute_bounding_box is False:
                dvi_machine.paint_char(registers.h, registers.v,
                                       char_bounding_box,
                                       glyph,
                                       dvi_font.magnification)
 
            else:

                print 'Char bounding box', char_bounding_box

                if bounding_box is None:
                    bounding_box = char_bounding_box
                else:
                    bounding_box |= char_bounding_box

            if self.set is True:
                registers.h += char_width

            print '%s char %3u "%s" width %8u h %10u' % (self.opcode_name,
                                                         char_code, chr(char_code),
                                                         char_width, registers.h)

        if compute_bounding_box is True:
            return bounding_box
            
###################################################

class Opcode_put_char(Opcode):

    ###############################################

    def __init__(self, char):

        super(Opcode_put_char, self).__init__(char, set = False)

#####################################################################################################

class Opcode_set_rule(Opcode):

    ###############################################

    def __init__(self, height, width, set = True):

        self.height = height
        self.width = width
        self.set = set

    ###############################################

    def __str__(self):

        if self.set is True:
            return 'set rule height %u width %u, h += width' % (self.height, self.width)
        else:
            return 'put rule height %u width %u' % (self.height, self.width)

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()

        if compute_bounding_box is False:
            dvi_machine.paint_rule(registers.h, registers.v, self.width, self.height)

        if compute_bounding_box is True:
            bounding_box = Interval2D([registers.h, registers.h + self.width]
                                      [registers.v, registers.v + self.height])

        if self.set is True:
            registers.h += self.width

        if compute_bounding_box is True:
            return bounding_box

###################################################

class Opcode_put_rule(Opcode_set_rule):

    ###############################################

    def __init__(self, height, width):

        super(Opcode_put_rule, self).__init__(height, width, set = False)

#####################################################################################################

class Opcode_push(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'push'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        dvi_machine.push_registers()

#####################################################################################################

class Opcode_pop(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'pop'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        dvi_machine.pop_registers()

#####################################################################################################

class Opcode_right(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        # Fixme: -> function

        return 'h += %+u sp %+.2f mm' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.h += self.x

#####################################################################################################

class Opcode_w0(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'h += w'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.h += registers.w

#####################################################################################################

class Opcode_w(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        return 'w = %+u sp %+.2f mm, h += w' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.w  = self.x
        registers.h += self.x

#####################################################################################################

class Opcode_x0(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'h += x'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.h += registers.x

#####################################################################################################

class Opcode_x(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        return 'x = %+u sp %+.2f mm, h += x' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.x  = self.x
        registers.h += self.x

#####################################################################################################

class Opcode_down(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        return 'v += %+u sp %+.2f mm' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.v += self.x

#####################################################################################################

class Opcode_y0(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'v += y'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.v += registers.y

#####################################################################################################
 
class Opcode_y(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        return 'y = %+u sp %+.2f mm, y += x' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.y  = self.x
        registers.h += self.x

#####################################################################################################

class Opcode_z0(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'v += z'

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.v += registers.z

#####################################################################################################

class Opcode_z(Opcode):

    ###############################################

    def __init__(self, x):

        self.x = x

    ###############################################

    def __str__(self):

        return 'z = %+u sp %+.2f mm, v += z' % (self.x, sp2mm(self.x))

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        registers = dvi_machine.get_registers()
        registers.z  = self.x
        registers.v += self.x

#####################################################################################################

class Opcode_font(Opcode):

    ###############################################

    def __init__(self, font_id):

        self.font_id = font_id

    ###############################################

    def __str__(self):

        return 'font %u' % (self.font_id)

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        dvi_machine.current_font = self.font_id

#####################################################################################################

class Opcode_xxx(Opcode):

    ###############################################

    def __init__(self, code):

        self.code = code

    ###############################################

    def __str__(self):

        return 'xxx [%s]' % (self.code)

    ###############################################

    def run(self, dvi_machine, compute_bounding_box = False):

        pass

#####################################################################################################

class DviFont(object):

    ###############################################

    def __init__(self, id, name, checksum, scale_factor, design_size):

        self.id = id
        self.name = name
        self.checksum = checksum
        self.scale_factor = scale_factor
        self.design_size = design_size

        self.magnification = fractions.Fraction(scale_factor, design_size)

    ###############################################

    def __str__(self):

        return '''Font ID %u
 - Name          %s
 - Checksum      %u
 - Design size   %u
 - Scale factor  %u
 - Magnification %u %%
''' % (self.id,
       self.name,
       self.checksum,
       self.scale_factor,
       self.design_size,
       self.magnification * 100)

    ###############################################

    def get_char_scaled_width(self, tfm_char):

        return tfm_char.get_scaled_width(self.scale_factor)

    ###############################################

    def get_char_scaled_height(self, tfm_char):

        return tfm_char.get_scaled_height(self.scale_factor)

    ###############################################

    def get_char_scaled_depth(self, tfm_char):

        return tfm_char.get_scaled_depth(self.scale_factor)

#####################################################################################################

class DviProgam(object):

    ###############################################

    def __init__(self):

        self.fonts = {} # dict of DviFont

        self.pages = []

    ###############################################

    def dvi_font_iterator(self):
        
        for font in self.fonts.values():
            yield font

    ###############################################

    def set_preambule_data(self,
                           comment,
                           dvi_format,
                           numerator, denominator, magnification):

        self.comment = comment
        self.dvi_format = dvi_format
        self.numerator, self.denominator, self.magnification = numerator, denominator, magnification

        # Fixme: use it to convert
        self.dvi_unit = fractions.Fraction(self.magnification * self.numerator, 1000 * self.denominator) # 1e-7 m

    ###############################################

    def set_postambule_data(self,
                            max_height, max_width,
                            stack_depth,
                            number_of_pages):

        self.max_height, self.max_width = max_height, max_width
        self.stack_depth = stack_depth
        self.number_of_pages = number_of_pages

        for i in xrange(self.number_of_pages):
            self.pages.append(OpcodeProgram())

    ###############################################
        
    def register_font(self, font):

        if self.fonts.has_key(font.id):
            pass 
            # print 'Font ID %u already registered' % (font.id)
        else:
            self.fonts[font.id] = font
        
    ###############################################

    def get_font(self, i):

        return self.fonts[i]

    ###############################################

    def get_page(self, i):

        return self.pages[i]

    ###############################################

    def print_summary(self):

        print '''DVI Program

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
''' % (self.comment,
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
        #     self.page_opcode_programs[i].print_program()

#####################################################################################################

one_in_in_sp = in2sp(1)

class DviMachineRegisters(object):

    ###############################################

    def __init__(self, h = one_in_in_sp, v = one_in_in_sp, w = 0, x = 0, y = 0, z = 0):

        self.h, self.v, self.w, self.x, self.y, self.z = h, v, w, x, y, z

    ###############################################

    def __str__(self):
        
        return '''
(h=+%10u sp %+10.2f mm v=+%10u sp %+10.2f mm
 w=+%10u sp %+10.2f mm x=+%10u sp %+10.2f mm
 y=+%10u sp %+10.2f mm z=+%10u sp %+10.2f mm)
''' % (self.h, sp2mm(self.h),
       self.v, sp2mm(self.v),
       self.w, sp2mm(self.w),
       self.x, sp2mm(self.x),
       self.y, sp2mm(self.y),
       self.z, sp2mm(self.z),
       )

    ###############################################

    def clone(self):

        return DviMachineRegisters(self.h, self.v, self.w, self.x, self.y, self.z)

#####################################################################################################

class DviMachine(object):
    
    ###############################################

    def __init__(self, font_map):

        self.font_manager = FontManager(font_map)

        self.fonts = {}

        self.reset()

    ###############################################

    def reset(self):

        self.current_font = None

        self.registers_stack = [DviMachineRegisters()]

    ###############################################

    def get_registers(self):

        return self.registers_stack[-1]

    ###############################################

    def push_registers(self):

        self.registers_stack.append(self.get_registers().clone())

    ###############################################

    def pop_registers(self):

        del self.registers_stack[-1]

    ###############################################

    def get_current_font(self):

        return self.fonts[self.current_font]

    ###############################################

    def get_current_dvi_font(self):

        return self.dvi_program.get_font(self.current_font)

    ###############################################

    def load_dvi_program(self, dvi_program):

        self.dvi_program = dvi_program

        self.load_dvi_fonts()

    ###############################################

    def load_dvi_fonts(self):

        # Load the Fonts
        for dvi_font in self.dvi_program.dvi_font_iterator():
            self.fonts[dvi_font.id] = self.font_manager.load_font(font_types.Pk, dvi_font.name) # Fixme

    ###############################################

    def run_page(self, page):

        opcode_program = self.dvi_program.get_page(page)

        print 'Program Length:', len(opcode_program)

        for opcode in opcode_program:
            print opcode
            opcode.run(self)
            print 'level %u' % (len(self.registers_stack)), self.get_registers()

    ###############################################

    def compute_page_bounding_box(self, page):

        opcode_program = self.dvi_program.get_page(page)

        print 'Program Length:', len(opcode_program)

        bounding_box = None

        for opcode in opcode_program:
            print opcode
            opcode_bounding_box = opcode.run(self, compute_bounding_box = True)
            print 'level %u' % (len(self.registers_stack)), self.get_registers()

            if opcode_bounding_box is not None:

                print 'Opcode bounding box', opcode_bounding_box

                if bounding_box is None:
                    bounding_box = opcode_bounding_box
                else:
                    bounding_box |= opcode_bounding_box
                
                print 'Current page bounding box', bounding_box

        print 'Page bounding box', bounding_box, 'sp'

        (x_min_mm, x_max_mm, y_min_mm, y_max_mm) = map(sp2mm, (bounding_box.x.inf, bounding_box.x.sup,
                                                               bounding_box.y.inf, bounding_box.y.sup))

        print '  [%.2f, %.2f]*[%.2f, %.2f] mm' % (x_min_mm, x_max_mm, y_min_mm, y_max_mm) 

        return bounding_box

    ###############################################

    def paint_rule(self, x, y, width, height):

        pass

    ###############################################

    def paint_char(self, x, y, char_bounding_box, glyph, magnification):

        pass

#####################################################################################################
#
# End
#
#####################################################################################################
