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
#  - 13/05/2010 fabrice To be implemented
#
####################################################################################################

####################################################################################################

####################################################################################################

from Stream import *
from OpcodeParser import *

####################################################################################################

class VfFontParser(OpcodeStreamParser, FileStream):

    opcode_definitions = (
        )
   
    ##############################################

    def __init__(self):

        super(VfFontParser, self).__init__(self.opcode_definitions)

        self.vf_font = None

####################################################################################################
#
# End
#
####################################################################################################
