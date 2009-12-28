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
#
#####################################################################################################

#####################################################################################################

__all__ = ['Encoding']

#####################################################################################################

import string

#####################################################################################################

from TextFile import *

#####################################################################################################

class Encoding(TextFile):

    ###############################################

    def __init__(self, filename):

        self.name = None

        self.glyph_indexes = []

        self.stop = False

        self.parse(filename)

        self.glyph_names = {}

        for i in xrange(len(self.glyph_indexes)):
            self.glyph_names[self.glyph_indexes[i]] = i
        
    ###############################################

    def parse_line(self, line):

        # print '[', line, ']'

        if self.name is None:
            
            if '[' in line:

                braket_index = line.index('[')

                word = line[line.index('/') +1 : braket_index]
                
                self.name = word.strip()

                line = line[braket_index +1:]

        if self.stop is False:

            if ']' in line: # ] def
                self.stop = True
                line = line[:line.index(']')]

            # print '  [', line, ']'

            words = filter(len,
                           map(lambda x: x.strip(),
                               string.split(line, sep = '/')))
            
            self.glyph_indexes.extend(words)

    ###############################################

    def print_summary(self):

        print '''
Encoding %s
''' % (self.name)

        for i in xrange(len(self.glyph_indexes)):
            print '%3i %s' % (i, self.glyph_indexes[i])

#####################################################################################################
#
# End
#
#####################################################################################################

