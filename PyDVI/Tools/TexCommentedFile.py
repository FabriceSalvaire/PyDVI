####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
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

