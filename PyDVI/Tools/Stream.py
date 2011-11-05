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
        
    """ Convert *x* to a fix word.  A fix word is a signed quantity, with the two's complement
    of the entire word used to represent negation.  Of the 32 bits in fix word, exactly 12 are
    to the left of the binary point: x -> x / 2**20.
    """

    return FIX_WORD_SCALE*float(x)

#####################################################################################################

class AbstractStream(object):

    """ Abstract class to read DVI, PK, TFM and VF streams.

    The followings methods are abstracts:

     * read
     * seek
     * tell
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

        """ Read *number_of_bytes* 8-bit characters from the optional position or the current
        position.  If *position* is not :obj:`None` then it seeks to the position specified.
        """

        if position is not None:
            self.seek(position)

        return self.read(number_of_bytes)

    ###############################################

    def read_byte_numbers(self, number_of_bytes, position=None):

        """ Read *number_of_bytes* 8-bit unsigned integers from the optional :obj:`position` or
        the current position (cf. :meth`read_bytes`).
        """

        return [ord(x) for x in self.read_bytes(number_of_bytes, position)]

    ###############################################

    def read_three_byte_numbers(self, position=None):

        """ Read three 8-bit unsigned integers from the optional position or the current position
        (cf. :meth`read_bytes`).
        """

        return self.read_byte_numbers(3, position)

    ###############################################

    def read_four_byte_numbers(self, position=None):

        """ Read four 8-bit unsigned integers from the optional position or the current position
        (cf. :meth`read_bytes`).
        """

        return self.read_byte_numbers(4, position)

    ###############################################

    def read_big_endian_number(self, number_of_bytes, signed=False, position=None):

        """ Read an (unsigned) integer encoded in big endian format with *number_of_bytes* bytes
        from the optional position or the current position (cf. :meth`read_bytes`).
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
        """ Read a 1-byte signed integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=1, signed=True, position=position)

    def read_signed_byte2(self, position=None):
        """ Read a 2-byte signed integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=2, signed=True, position=position)

    def read_signed_byte3(self, position=None):
        """ Read a 3-byte signed integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=3, signed=True, position=position) 

    def read_signed_byte4(self, position=None):
        """ Read a 4-byte signed integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=4, signed=True, position=position)

    def read_unsigned_byte1(self, position=None):
        """ Read a 1-byte unsigned integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=1, signed=False, position=position)

    def read_unsigned_byte2(self, position=None):
        """ Read a 2-byte unsigned integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=2, signed=False, position=position)

    def read_unsigned_byte3(self, position=None):
        """ Read a 3-byte unsigned integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=3, signed=False, position=position)

    def read_unsigned_byte4(self, position=None):
        """ Read a 4-byte unsigned integer (cf. :meth:`read_big_endian_number`). """ 
        return self.read_big_endian_number(number_of_bytes=4, signed=False, position=position)

    read_unsigned_byten = (read_unsigned_byte1, 
                           read_unsigned_byte2,
                           read_unsigned_byte3,
                           read_unsigned_byte4)

    read_signed_byten = (read_signed_byte1, 
                         read_signed_byte2,
                         read_signed_byte3,
                         read_signed_byte4)

    ###############################################

    def read_fix_word(self, position=None):
        
        """ Read a fix word from the optional position or the current position.
        """

        return self.to_fix_word(self.read_signed_byte4(position))

    ###############################################

    def read_bcpl(self, position=None):
        
        """ Read a BCPL string from the optional position or the current position.

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

        """ Seek to position,
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
