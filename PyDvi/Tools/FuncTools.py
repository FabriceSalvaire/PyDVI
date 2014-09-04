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
#                                              Audit
#
# - 17/12/2011 Fabrice
#   xx
#
####################################################################################################

__all__ = ['repeat_call', 'get_filename_extension']

####################################################################################################

def repeat_call(func, count):

    """ Call the function *func* *count* times and return the output as a list. """

    return [func() for i in xrange(count)]

####################################################################################################

def get_filename_extension(filename):

    """ Return the filename extension. """

    index = filename.rfind('.')
    if index >= 0:
        try:
            return filename[index+1:]
        except:
            return None
    else:    
        return None

####################################################################################################

def sign_of(x):
    """ Return the sign of a number. """
    if x < 0:
        return -1
    else:
        return 1

# def sign(x):
#     return cmp(x, 0)

####################################################################################################

def middle(a, b):
    return .5 * (a + b)

####################################################################################################
#
# End
#
####################################################################################################
 
