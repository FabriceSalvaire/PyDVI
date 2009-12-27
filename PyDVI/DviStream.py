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
#  - 26/12/2009 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['DviFileStream']

#####################################################################################################

import mmap

#####################################################################################################

FIX_WORD_SCALE = 1./2**20

#####################################################################################################

class DviStream(object):

    ###############################################

    def read_bytes(self, number_of_bytes, position = None):

        '''
        Read n number of bytes from the optional position or the current position
        '''

        if position is None:
            start_position = self.tell()
        else:
            self.seek(position)

        return self.stream.read(number_of_bytes)

    ###############################################

    def read_byte_numbers(self, number_of_bytes, position = None):
        '''
        Read n byte numbers from the optional position or the current position
        '''

        return map(ord, self.read_bytes(number_of_bytes, position))

    ###############################################

    def read_four_byte_numbers(self, position = None):

        '''
        Read four byte numbers from the optional position or the current position
        '''

        return self.read_byte_numbers(4, position)

    ###############################################

    def read_big_endian_number(self, number_of_bytes, signed = False, position = None):

        '''
        Read a number coded in big endian format from the DVI input stream
        '''

        # This code can be unrolled

        bytes = self.read_byte_numbers(number_of_bytes, position)

        number = bytes[0]

        if signed is True and number >= 128:
            number -= 256

        for i in xrange(1, number_of_bytes):
            number *= 256
            number += bytes[i]

        return number

    ###############################################
            
    def read_signed_byte1(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 1, signed = True, position = position)

    def read_signed_byte2(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 2, signed = True, position = position)

    def read_signed_byte3(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 3, signed = True, position = position) 

    def read_signed_byte4(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 4, signed = True, position = position)

    def read_unsigned_byte1(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 1, signed = False, position = position)

    def read_unsigned_byte2(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 2, signed = False, position = position)

    def read_unsigned_byte3(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 3, signed = False, position = position)

    def read_unsigned_byte4(self, position = None):
        return self.read_big_endian_number(number_of_bytes = 4, signed = False, position = position)

    read_unsigned_byten = (read_unsigned_byte1, 
                           read_unsigned_byte2,
                           read_unsigned_byte3,
                           read_unsigned_byte4)

    read_signed_byten = (read_signed_byte1, 
                         read_signed_byte2,
                         read_signed_byte3,
                         read_signed_byte4)

    ###############################################

    def read_fix_word(self, position = None):
        
        '''
        Read a fiw word from the optional position or the current position
        '''

        # A fix word is a signed quantity, with the two's complement of the entire word used to
        # represent negation.  Of the 32 bits in fix word, exactly 12 are to the left of the binary
        # point.

        return FIX_WORD_SCALE*float(self.read_signed_byte4(position))

    ###############################################

    def read_bcpl(self, position = None):
        
        '''
        Read a BCPL string from the optional position or the current position
        '''

        return self.read_bytes(self.read_unsigned_byte1(position))

    ###############################################

    def repeat(self, method, count):
        
        sequence = []
        
        for i in xrange(count):
            sequence.append(method())
            
        return sequence

#####################################################################################################

class DviFileStream(DviStream):
    
    ###############################################

    def open(self, filename):

        self.file = open(filename, 'rb')

        self.stream = mmap.mmap(self.file.fileno(), length = 0, access = mmap.ACCESS_READ)

        self.stream.seek(0)

    ###############################################

    def close(self):

        self.stream.close()
        self.file.close()

    ###############################################

    def seek(self, postion):

        '''
        Seek to position
        '''

        self.stream.seek(postion)

    ###############################################

    def tell(self):

        '''
        Tell the current position
        '''

        return self.stream.tell()

#####################################################################################################
#
# End
#
#####################################################################################################
