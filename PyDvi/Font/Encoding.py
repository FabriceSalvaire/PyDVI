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
#  - 10/10/2011 Fabrice
#
####################################################################################################

"""
This module handles TeX encoding file.

An encoding file map the glyph index with its symbolic name. It uses the ``.enc`` extension.

For example, the content of :file:`cork.enc` is::

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

The content of this file can be parsed using::

  cork_encoding = Encoding('/usr/share/texmf/fonts/enc/dvips/base/cork.enc')

The encoding's name can be retrieved using::

  >>> cork_encoding.name
  'CorkEncoding'

The number of glyphes can be obtained using the function :func:`len`::

  >>> len(cork_encoding)
  256

The index of the glyph ``eth`` can be retrieved using::

  >>> cork_encoding['eth']
  0xF0

and reciprocally::

  >>> cork_encoding[0xF0]
  'eth'

The methods :meth:`to_index` and :meth:`to_name` are used internally for this purpose.
"""

####################################################################################################

__all__ = ['Encoding']

####################################################################################################

from ..Tools.Logging import print_card
from ..Tools.TexCommentedFile import TexCommentedFile

####################################################################################################

class Encoding(object):

    """
    Parse an encoding file and store the association between the index and the glyph's name.

    Public attributes are:

      ``name``
    """

    ##############################################

    def __init__(self, filename):

        self.name = None

        self._glyph_indexes = [] # Map glyph index to glyph name
        self._glyph_names = {} # Map glyph name  to glyph index

        try:
            with TexCommentedFile(filename) as encoding_file:
                content = encoding_file.concatenate_lines()
                open_braket_index = content.index('[')
                close_braket_index = content.index(']')
                self._parse_name(content[:open_braket_index])
                self._parse_glyph_names(content[open_braket_index+1:close_braket_index])
        except:
            raise NameError('Bad encoding file')

        # Init glyph_names dict
        for i in xrange(len(self._glyph_indexes)):
            self._glyph_names[self._glyph_indexes[i]] = i

    ##############################################

    def __len__(self):

        """ Return the number of glyphes. """

        return len(self._glyph_indexes)        

    ##############################################

    def __getitem__(self, index):

        """ If *index* is a glyph index then return the corresponding symbolic name else try to
        return the glyph index corresponding to the symbolic name *index*.
        """

        try:
            return self.to_name(int(index))
        except ValueError:
            return self.to_index(index)

    ##############################################

    def _parse_name(self, line):

        """ Find the encoding name at the left of the line, as '/CorkEncoding'. """

        # try
        name_start_index = line.index('/')
        self.name = line[name_start_index +1:].strip()

    ##############################################

    def _parse_glyph_names(self, line):

        """ Find glyph names in *line*, as '/grave /acute /circumflex ...'. """

        for word in line.split('/'):
            word = word.strip()
            if word:
                self._glyph_indexes.append(word)

    ##############################################

    def to_name(self, i):

        """ Return the symbolic name corresponding to the glyph index *i*. """

        return self._glyph_indexes[i]

    ##############################################

    def to_index(self, name):

        """ Return the glyph index corresponding to the symbolic name. """

        return self._glyph_names[name]

    ##############################################

    def print_summary(self):

        message = 'Encoding %s:\n\n' % (self.name)
        for i in xrange(len(self)):
            message += '| %3i | %s\n' % (i, self.to_name(i))

        print_card(message)

####################################################################################################
#
# End
#
####################################################################################################

