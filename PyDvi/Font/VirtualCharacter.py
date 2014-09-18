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

__all__ = ['VirtualCharacter']

####################################################################################################

from ..Tools.Stream import ByteStream

####################################################################################################

class VirtualCharacter(object):

    ##############################################

    def __init__(self, char_code, width, dvi):

        self.char_code = char_code
        self.width = width
        self._dvi = dvi
        self._subroutine = None

    ##############################################

    def __repr__(self):

        return "Virtual Character {}".format(self.char_code)

    ##############################################

    @property
    def subroutine(self):

        if self._subroutine is None:
            from ..Dvi.DviParser import DviSubroutineParser # Fixme: circular import ?
            parser = DviSubroutineParser(ByteStream(self._dvi))
            self._subroutine = parser.parse()
        return self._subroutine

####################################################################################################
#
# End
#
####################################################################################################
