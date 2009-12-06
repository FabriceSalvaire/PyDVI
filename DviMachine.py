#####################################################################################################

import string

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

        pass

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

        return 'h += %u' %  (self.x)

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

        return 'w = %u, h += w' % (self.x)

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

        return 'x = %u, h += x' % (self.x)

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

        return 'v += %u' % (self.x)

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

        return 'y = %u, y += x' % (self.x)

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

        return 'z = %u, v += z' % (self.x)

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

        dvi_machine.font = self.font_id

#####################################################################################################

class Opcode_xxx(Opcode):

    ###############################################

    def __init__(self, code):

        self.code = code

    ###############################################

    def __str__(self):

        return 'xxx', self.opcode

    ###############################################

    def run(self, dvi_machine):

        pass

#####################################################################################################

class DviMachineRegisters(object):

    ###############################################

    def __init__(self, h = 0, v = 0, w = 0, x = 0, y = 0, z = 0):

        self.h, self.v, self.w, self.x, self.y, self.z = h, v, w, x, y, z

    ###############################################

    def __str__(self):

        return '(h=%u v=%u w=%u x=%u y=%u z=%u)' % (self.h, self.v, self.w, self.x, self.y, self.z)

    ###############################################

    def duplicate(self):

        return DviMachineRegisters(self.h, self.v, self.w, self.x, self.y, self.z)

class DviMachine(object):
    
    ###############################################

    def __init__(self):

        self.reset()

    ###############################################

    def reset(self):

        self.font = None

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

    def run(self, opcode_program):

        for opcode in opcode_program:
            print opcode
            opcode.run(self)
            print 'level %u' % (len(self.registers_stack)), self.registers()

#####################################################################################################
#
# End
#
#####################################################################################################
