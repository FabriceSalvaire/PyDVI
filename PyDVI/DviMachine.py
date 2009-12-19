#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################

import fractions
import string

#####################################################################################################

from FontManager import FontManager
from TeXUnit import *

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

class Opcode_put_char(Opcode):

    ###############################################

    def __init__(self, char):

        self.char = char

    ###############################################

    def __str__(self):

        return 'put char "%s"' % (chr(self.char))

    ###############################################

    def run(self, dvi_machine):

        pass

#####################################################################################################

class Opcode_set_char(Opcode):

    ###############################################

    def __init__(self, char):

        self.characters = [char]

    ###############################################

    def __str__(self):

        return 'set char "%s"' % (string.join(map(chr, self.characters), sep = ''))
        # return 'set char "%s"' % str(self.characters)

    ###############################################

    def append(self, char):

        self.characters.append(* char)

    ###############################################

    def run(self, dvi_machine):

        current_font = dvi_machine.get_current_font()

        for char_code in self.characters:

            glyph = current_font.get_glyph(char_code)
            
            glyph.print_summary()

            # Fixme: factor .75 ?
            #   use read_fix_word from TFM
            #     width = tfm * font_size = .75 * 65535

            dvi_font = dvi_machine.dvi_program.get_font(dvi_machine.current_font)

            tfm = glyph.tfm * dvi_font.scale_factor / (1 << 20)

            print 'set char %u "%s" width %u' % (char_code, chr(char_code), tfm)

#####################################################################################################

class Opcode_put_rule(Opcode):

    ###############################################

    def __init__(self, height, width):

        self.height = height
        self.width = width

    ###############################################

    def __str__(self):

        return 'put rule height %u width %u' % (self.height, self.width)

    ###############################################

    def run(self, dvi_machine):

        pass

#####################################################################################################

class Opcode_set_rule(Opcode_put_rule):

    ###############################################

    def __init__(self, height, width):

        super(Opcode_set_rule, self).__init__(height, width)

    ###############################################

    def __str__(self):

        return 'set rule height %u width %u, h += width' % (self.height, self.width)

    ###############################################

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
        registers.h += self.width

#####################################################################################################

class Opcode_push(Opcode):

    ###############################################

    def __init__(self):

        pass

    ###############################################

    def __str__(self):

        return 'push'

    ###############################################

    def run(self, dvi_machine):

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

    def run(self, dvi_machine):

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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

        registers = dvi_machine.registers()
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

    def run(self, dvi_machine):

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

    def run(self, dvi_machine):

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

    ###############################################

    def __str__(self):

        return '''Font ID %u
 - Name         %s
 - Checksum     %u
 - Scale factor %u
 - Design size  %u
''' % (self.id,
       self.name,
       self.checksum,
       self.scale_factor,
       self.design_size)

#####################################################################################################

class DviProgam(object):

    ###############################################

    def __init__(self):

        self.fonts = {}

        self.pages = []

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
            print 'Font ID %u already registered' % (font.id)
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
''' % (
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

        for font in self.fonts.values():
            print font

        # for i in xrange(self.number_of_pages):
        #     print '\nPage', i
        #     self.page_opcode_programs[i].print_program()

#####################################################################################################

class DviMachineRegisters(object):

    ###############################################

    def __init__(self, h = 0, v = 0, w = 0, x = 0, y = 0, z = 0):

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

    def duplicate(self):

        return DviMachineRegisters(self.h, self.v, self.w, self.x, self.y, self.z)

#####################################################################################################

class DviMachine(object):
    
    ###############################################

    def __init__(self):

        self.font_manager = FontManager()

        self.fonts = {}

        self.reset()

    ###############################################

    def reset(self):

        self.current_font = None

        self.registers_stack = [DviMachineRegisters()]

    ###############################################

    def registers(self):

        return self.registers_stack[-1]

    ###############################################

    def push_registers(self):

        self.registers_stack.append(self.registers().duplicate())

    ###############################################

    def pop_registers(self):

        del self.registers_stack[-1]

    ###############################################

    def get_current_font(self):

        return self.fonts[self.current_font]

    ###############################################

    def run(self, dvi_program, page):

        self.dvi_program = dvi_program

        for font in dvi_program.fonts.values():
            self.fonts[font.id] = self.font_manager.load_font(FontManager.Pk, font.name)

        opcode_program = dvi_program.get_page(page)

        for opcode in opcode_program:
            print opcode
            opcode.run(self)
            print 'level %u' % (len(self.registers_stack)), self.registers()

#####################################################################################################
#
# End
#
#####################################################################################################
