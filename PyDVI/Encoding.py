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
#  - 10/01/2010 fabrice
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['Encoding']

#####################################################################################################

from Logging import print_card
from TextFile import TextFile

#####################################################################################################
#
# Example from /usr/share/texmf-texlive/fonts/enc/dvips/base/cork.enc
#
# /CorkEncoding [          % now 256 chars follow
# % 0x00
#   /grave /acute /circumflex /tilde /dieresis /hungarumlaut /ring /caron
#   ...
#   /oslash /ugrave /uacute /ucircumflex /udieresis /yacute /thorn /germandbls
# ] def
#
#####################################################################################################

class Encoding(object):

    """The Encoding class parse an encoding file and store the association between the index and the
    glyph's name.
    """

    ###############################################

    def __init__(self, filename):

        """Create an Encoding instance.
        """

        self.name = None

        self.glyph_indexes = [] # Map glyph index to glyph name
        self.glyph_names   = {} # Map glyph name  to glyph index

        try:
            text_file = TextFile(filename)
            for line in text_file:
                if self.__parse_line(line):
                    break
        except:
            raise NameError('Bad encoding file')

        # Init glyph_names dict
        for i in xrange(len(self.glyph_indexes)):
            self.glyph_names[self.glyph_indexes[i]] = i

    ###############################################

    def __len__(self):

        return len(self.glyph_indexes)        
        
    ###############################################

    def __parse_line(self, line):

        stop = False

        if self.name is None:
            # try
            braket_index = line.index('[')
            self.__parse_name(line[:braket_index])    
            line = line[braket_index +1:]
            
        braket_index = line.find(']')
        if braket_index != -1: # mathch '] def'
            stop = True
            line = line[:braket_index]

        self.__parse_glyph_names(line)
        
        return stop

    ###############################################

    def __parse_name(self, line):

        """Find '\CorkEncoding' at the left of the line
        """

        # try
        name_start_index = line.index('/')
        self.name = line[name_start_index +1:].strip()

    ###############################################

    def __parse_glyph_names(self, line):

        """Find glyph names in '/grave /acute /circumflex ...'
        """

        for word in line.split('/'):
            word = word.strip()
            if word:
                self.glyph_indexes.append(word)

    ###############################################

    def print_summary(self):

        message = '''Encoding %s
''' % (self.name)

        for i in xrange(len(self.glyph_indexes)):
            message += '%3i | %s\n' % (i, self.glyph_indexes[i])

        print_card(message)

#####################################################################################################
#
# End
#
#####################################################################################################

