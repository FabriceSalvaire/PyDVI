#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2011 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
#                                              Audit
#
# - 17/12/2011 Fabrice
#   xx
#
#####################################################################################################

__all__ = ['repeat_call', 'get_filename_extension']

#####################################################################################################

def repeat_call(func, count):

    """ Call the function *func* *count* times and return the output as a list. """

    return [func() for i in xrange(count)]

#####################################################################################################

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

#####################################################################################################

def sign_of(x):
    """ Return the sign of a number. """
    if x < 0:
        return -1
    else:
        return 1

#####################################################################################################
#
# End
#
#####################################################################################################
 