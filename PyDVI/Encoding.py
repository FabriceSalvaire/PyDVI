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
#  - 10/10/2011 Fabrice
#
#####################################################################################################

"""
This module handles TeX encoding file.

An encoding file map the glyph index with its symbolic name. It uses the ".enc" extension. For
example, the content of :file:"cork.enc" is::

  /CorkEncoding [ % now 256 chars follow
  % 0x00
    /grave /acute /circumflex /tilde /dieresis /hungarumlaut /ring /caron
    /breve /macron /dotaccent /cedilla
    /ogonek /quotesinglbase /guilsinglleft /guilsinglright
  ...
  % 0xF0
    /eth /ntilde /ograve /oacute /ocircumflex /otilde /odieresis /oe
    /oslash /ugrave /uacute /ucircumflex /udieresis /yacute /thorn /germandbls
  ] def

The percent character is used for comment as for TeX.
"""

#####################################################################################################

__all__ = ['Encoding']

#####################################################################################################

from Tools.Logging import print_card
from Tools.TexCommentedFile import TexCommentedFile

#####################################################################################################

class Encoding(object):

    """Parse an encoding file and store the association between the index and the glyph's name.
    """

    ###############################################

    def __init__(self, filename):

        self.name = None

        self.glyph_indexes = [] # Map glyph index to glyph name
        self.glyph_names   = {} # Map glyph name  to glyph index

        try:
            with TexCommentedFile(filename) as encoding_file:
                content = encoding_file.concatenate_lines()
                open_braket_index = content.index('[')
                close_braket_index = content.index(']')
                self.__parse_name(content[:open_braket_index])
                self.__parse_glyph_names(content[open_braket_index+1:close_braket_index])
        except:
            raise NameError('Bad encoding file')

        # Init glyph_names dict
        for i in xrange(len(self.glyph_indexes)):
            self.glyph_names[self.glyph_indexes[i]] = i

    ###############################################

    def __len__(self):

        return len(self.glyph_indexes)        

    ###############################################

    def __parse_name(self, line):

        """Find '/CorkEncoding' at the left of the line
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

        message = 'Encoding %s\n' % (self.name)
        for i in xrange(len(self.glyph_indexes)):
            message += '%3i | %s\n' % (i, self.glyph_indexes[i])

        print_card(message)

#####################################################################################################
#
# End
#
#####################################################################################################

