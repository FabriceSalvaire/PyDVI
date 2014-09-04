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
#  - 10/10/2011 fabrice
#
####################################################################################################

####################################################################################################

__all__ = ['TexCommentedFile']

####################################################################################################

class TexCommentedFile(file):

    """ This class permits to iterate over lines of a text file and to skip commented line by '%'.
    """

    ##############################################

    def __init__(self, filename):

        super(TexCommentedFile, self).__init__(filename, mode='r')

    ##############################################

    def __iter__(self):

        while True:
            line = self.readline()
            if not line:
                raise StopIteration()
            comment_start_index = line.find('%')
            if comment_start_index != -1:
                line = line[:comment_start_index]
            line = line.strip()
            if line:
                yield line

    ##############################################

    def concatenate_lines(self):

        """ Concatenate the lines and return the corresponding string. """

        return ''.join(self)

####################################################################################################
#
# End
#
####################################################################################################

