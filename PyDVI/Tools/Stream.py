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
# - 31/10/2011 fabrice
#  - Check FileStream design.
#  - Use context manager ?
#  - read_unsigned_byten is badly displayed in doc
#
#####################################################################################################

#####################################################################################################

__all__ = ['AbstractStream', 'StandardStream', 'FileStream', 'to_fix_word']

#####################################################################################################

import mmap
import os

#####################################################################################################

FIX_WORD_SCALE = 1./2**20

def to_fix_word(x):
        
    """ Convert *x* to a fix word.

    A fix word is a 32-bit representation of a binary fraction.  A fix word is a signed quantity,
    with the two's complement of the entire word used to represent negation.  Of the 32 bits in a
    fix word, exactly 12 are to the left of the binary point; thus, the largest fix word value is
    2048 - 2**-20, and the smallest is -2048.

    ``fix word = x / 2**20``
    """

    return FIX_WORD_SCALE*float(x)

#####################################################################################################

class AbstractStream(object):

    """ Abstract class to read DVI, PK, TFM and VF streams.

    The followings methods are abstracts:

     * :meth:`read`
     * :meth:`seek`
     * :meth:`tell`

    and must be implemented in subclass.

    In the followings methods, the *position* argument is used to specify a position in the stream
    for the read operation.  If *position* is not :obj:`None`, it seeks to the specified position
    before to read the stream else it reads from the current position.  See also :meth:`read_bytes`.
    """

    ###############################################

    def read(self, number_of_bytes):

        """ Read *n* bytes from the current position.
        """

        raise NotImplementedError

    ###############################################

    def seek(self, postion, whence):

        """ Seek to position.
        """

        raise NotImplementedError

    ###############################################

    def tell(self):

        """ Tell the current position.
        """

        raise NotImplementedError

    ###############################################

    def read_bytes(self, number_of_bytes, position=None):

        """ Read *number_of_bytes* bytes from the optional position or the current position. If
        *position*, it seeks to the specified position and thus change the current position in the
        stream.
        """

        if position is not None:
            self.seek(position)

        return self.read(number_of_bytes)

    ###############################################

    def read_byte_numbers(self, number_of_bytes, position=None):

        """ Read *number_of_bytes* times 8-bit unsigned integers, cf. :meth:`read_bytes`.
        """

        return [ord(x) for x in self.read_bytes(number_of_bytes, position)]

    ###############################################

    def read_three_byte_numbers(self, position=None):

        """ Read three 8-bit unsigned integers, cf. :meth:`read_bytes`.
        """

        return self.read_byte_numbers(3, position)

    ###############################################

    def read_four_byte_numbers(self, position=None):

        """ Read four 8-bit unsigned integers, cf. :meth:`read_bytes`.
        """

        return self.read_byte_numbers(4, position)

    ###############################################

    def read_big_endian_number(self, number_of_bytes, signed=False, position=None):

        """ Read a signed or an unsigned integer encoded in big endian order with *number_of_bytes*
        bytes, cf. :meth:`read_bytes`.
        """

        # This code can be unrolled

        bytes = self.read_byte_numbers(number_of_bytes, position)

        number = bytes[0]
        if signed and number >= 128:
            number -= 256
        for i in xrange(1, number_of_bytes):
            number *= 256
            number += bytes[i]

        return number

    ###############################################
            
    def read_signed_byte1(self, position=None):
        """ Read a 1-byte signed integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=1, signed=True, position=position)

    def read_signed_byte2(self, position=None):
        """ Read a 2-byte signed integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=2, signed=True, position=position)

    def read_signed_byte3(self, position=None):
        """ Read a 3-byte signed integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=3, signed=True, position=position) 

    def read_signed_byte4(self, position=None):
        """ Read a 4-byte signed integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=4, signed=True, position=position)

    def read_unsigned_byte1(self, position=None):
        """ Read a 1-byte unsigned integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=1, signed=False, position=position)

    def read_unsigned_byte2(self, position=None):
        """ Read a 2-byte unsigned integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=2, signed=False, position=position)

    def read_unsigned_byte3(self, position=None):
        """ Read a 3-byte unsigned integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=3, signed=False, position=position)

    def read_unsigned_byte4(self, position=None):
        """ Read a 4-byte unsigned integer, cf. :meth:`read_big_endian_number`. """ 
        return self.read_big_endian_number(number_of_bytes=4, signed=False, position=position)

    read_unsigned_byten = (read_unsigned_byte1, 
                           read_unsigned_byte2,
                           read_unsigned_byte3,
                           read_unsigned_byte4)
    """ This tuple permits to get the read_unsigned_byte method with the number of bytes as index.
    """

    read_signed_byten = (read_signed_byte1, 
                         read_signed_byte2,
                         read_signed_byte3,
                         read_signed_byte4)
    """ This tuple permits to get the *read_signed_byte* method with the number of bytes as index.
    """

    ###############################################

    def read_fix_word(self, position=None):
        
        """ Read a fix word.
        """

        return to_fix_word(self.read_signed_byte4(position))

    ###############################################

    def read_bcpl(self, position=None):
        
        """ Read a BCPL string.

        The BCPL string format comes from the Basic Combined Programming Language.  The length of
        the string is given by the first byte, thus its length is limited to 256 characters.
        """

        return self.read_bytes(self.read_unsigned_byte1(position))

#####################################################################################################

class StandardStream(AbstractStream):

    """ Abstract stream class.

    The attribute :attr:`stream` must be defined in subclass.
    """

    ###############################################

    def read(self, number_of_bytes):

        """ Read *n* bytes from the current position.
        """

        # print 'Stream.read %u bytes at %u' % (number_of_bytes, self.tell())

        bytes = self.stream.read(number_of_bytes)

        # print '  bytes:', map(ord, bytes)

        return bytes

    ###############################################

    def seek(self, postion, whence=os.SEEK_SET):

        """ Seek to position.
        """

        self.stream.seek(postion, whence)

    ###############################################

    def tell(self):

        """ Tell the current position.
        """

        return self.stream.tell()

#####################################################################################################

class FileStream(StandardStream):
    
    ###############################################

    def __init__(self, filename):

        self.file = open(filename, 'rb')
        self.stream = mmap.mmap(self.file.fileno(), length=0, access=mmap.ACCESS_READ)
        self.seek(0)

    ###############################################

    def __del__(self):

        self.stream.close()
        self.file.close()

#####################################################################################################
#
# End
#
#####################################################################################################
