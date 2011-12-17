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
#  - 16/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['OpcodeParserSet', 'OpcodeParser']

#####################################################################################################

from PyDVI.Tools.Stream import AbstractStream

#####################################################################################################

def sign_of(x):
    
    if x < 0:
        return -1
    else:
        return 1

#####################################################################################################

class OpcodeParser(object):

    ###############################################

    def __init__(self, opcode, name, description, parameters=(), opcode_class=None):

        """
        Opcode Parser
        """

        self.opcode = opcode
        self.name = name
        self.description = description
        self.opcode_class = opcode_class

        self.parameter_readers = []
        if parameters:
            self._init_parameter_readers(parameters)

    ###############################################

    def _init_parameter_readers(self, parameters):

        for number_of_bytes in parameters:
            if parameters > 0:
                read_byten = AbstractStream.read_unsigned_byten
            else:
                read_byten = AbstractStream.read_signed_byten
            self.parameter_readers.append(read_byten[abs(number_of_bytes) -1])

    ###############################################

    def __str__(self):

        return 'opcode %3u %s %s' % (self.opcode, self.name, self.description)

    ###############################################

    def read_parameters(self, opcode_parser):

        return [parameter_reader(opcode_parser.stream) for parameter_reader in self.parameter_readers]

    ###############################################

    def to_opcode(self, args):

        if self.opcode_class is not None:
            return self.opcode_class(* args)
        else:
            return None

#####################################################################################################

class OpcodeParserSet(list):
    
    ###############################################

    def __init__(self, opcode_definitions):

        """
        Opcode Set

        opcode_definitions : (opcode_definition, ...)

        opcode_definition : 
          (opcode_indexes, opcode_name, opcode_description, opcode_parameters=(), opcode_class=None) |
          (opcode_indexes, opcode_parser_class),

        opcode_indexes :
          index |
          [lower_index, upper_index] # duplicate the opcode in the range

        opcode_parameters :
          (p0, p1, ...) |
          ([lower_n, upper_n]) # opcode at [index + i] has parameter p[i]

        """

        # Allocate 256 opcode
        self.extend([None]*256)
        for opcode_definition in opcode_definitions:
            self._init_opcode_parser(opcode_definition)

    ###############################################

    def _init_opcode_parser(self, opcode_definition):

        # opcode index

        index = opcode_definition[0]
        if isinstance(index, list):
            indexes = range(index[0], index[1] +1)
        else:
            indexes = [index]

        if isinstance(opcode_definition[1], OpcodeParser.__class__):
            for i in indexes:
                self[i] = opcode_definition[1](i)

        else: # opcode description string
            name, description, parameters, opcode_class = opcode_definition[1:]
        
            if isinstance(parameters, list):
                lower_n, upper_n = parameters
                signe = sign_of(lower_n)
                for n in xrange(abs(lower_n), abs(upper_n) +1):
                    i = index + n -1 # Fixme: bad: index vs indexes
                    self[i] = OpcodeParser(i, name, description, tuple([signe*n]), opcode_class)

            else:
                for i in indexes:
                    self[i] = OpcodeParser(i, name, description, parameters, opcode_class)

        # for opcode_parser in self:
        #    print opcode_parser

#####################################################################################################
#
# End
#
#####################################################################################################
