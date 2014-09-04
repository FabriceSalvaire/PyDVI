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
#  - 16/01/2010 fabrice
#
####################################################################################################

""" This modules provides tools to parse TeX stream like DVI file and PK Font.
"""

####################################################################################################

__all__ = ['OpcodeParserSet', 'OpcodeParser']

####################################################################################################

from .Tools.FuncTools import sign_of
from .Tools.Stream import AbstractStream

####################################################################################################

class OpcodeParser(object):

    """ This class implements an opcode parser. """

    ##############################################

    def __init__(self, opcode, name, description, parameters=(), opcode_class=None):

        """ The argument *opcode* defines the opcode byte.

        The argument *name* and *description* defines the name and a description string, respectively.

        The argument *parameters* is a tuple that defines the parameters of the opcode.  Each item
        is an integer that gives the number of bytes of the parameter.  If this number is negative
        then the parameter is a signed integer.  For example ``(2, -3)`` defines an opcode having as
        parameters a 2-byte unsigned integer followed by a 3-byte signed integer.

        The optional *opcode_class* defines an :class:`PyDvi.DviMachine.Opcode` subclass for the
        opcode.
        """

        self.opcode = opcode
        self.name = name
        self.description = description
        self.opcode_class = opcode_class

        self.parameter_readers = []
        if parameters:
            self._init_parameter_readers(parameters)

    ##############################################

    def _init_parameter_readers(self, parameters):

        for number_of_bytes in parameters:
            if number_of_bytes > 0:
                read_byten = AbstractStream.read_unsigned_byten
            else:
                read_byten = AbstractStream.read_signed_byten
            self.parameter_readers.append(read_byten[abs(number_of_bytes) -1])

    ##############################################

    def __str__(self):

        return 'opcode %3u %s %s' % (self.opcode, self.name, self.description)

    ##############################################

    def read_parameters(self, opcode_parser):

        """ Read the opcode parameters. """

        return [parameter_reader(opcode_parser.stream) for parameter_reader in self.parameter_readers]

    ##############################################

    def to_opcode(self, args):

        """ Return an an :class:`PyDvi.DviMachine.Opcode` subclass isntance. """

        if self.opcode_class is not None:
            return self.opcode_class(* args)
        else:
            return None

####################################################################################################

class OpcodeParserSet(list):

    """ This class defines an opcode parser set. """
    
    ##############################################

    def __init__(self, opcode_definitions):

        """ The parameter *opcode_definitions* is a tuple of 'opcode definition'.

        An opcode definition is a tuple that corresponds to the parameters of the
        :class:`OpcodeParser` constructor.  Except that the opcode byte can be a list that defines a
        range of opcode bytes.  In this case the opcode is duplicated in the opcode range.  Moreover
        the parameter's definition can be a list that defines a range for a mono parameter set of
        opcodes.  For example ``[1,4]`` will create successively an opcode with 1 to 4-byte unsigned
        parameter with an incremental opcode byte starting from the one specified.
        
        Usage summary::

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

        super(OpcodeParserSet, self).__init__()

        # Allocate 256 opcode
        self.extend([None]*256)
        for opcode_definition in opcode_definitions:
            self._init_opcode_parser(opcode_definition)

    ##############################################

    def _init_opcode_parser(self, opcode_definition):

        """ Build the set. """

        opcode_index = opcode_definition[0]
        if isinstance(opcode_index, list):
            opcode_indexes = range(opcode_index[0], opcode_index[1] +1)
        else:
            opcode_indexes = [opcode_index]

        if isinstance(opcode_definition[1], OpcodeParser.__class__):
            opcode_parser_class = opcode_definition[1]
            for i in opcode_indexes:
                self[i] = opcode_parser_class(i)

        else: # opcode description string
            name, description, parameters, opcode_class = opcode_definition[1:]
        
            if isinstance(parameters, list):
                lower_n, upper_n = parameters
                signe = sign_of(lower_n)
                for n in xrange(abs(lower_n), abs(upper_n) +1):
                    i = opcode_index + n -1 # Fixme: bad: opcode_index vs opcode_indexes
                    self[i] = OpcodeParser(i, name, description, tuple([signe*n]), opcode_class)

            else:
                for i in opcode_indexes:
                    self[i] = OpcodeParser(i, name, description, parameters, opcode_class)

####################################################################################################
#
# End
#
####################################################################################################
