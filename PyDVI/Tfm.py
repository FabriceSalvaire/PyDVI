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
# - 11/12/2011 fabrice
#   - why ref Tfm, self registration
#
#   - why int is scaled_...
#   - TfmChar -> Char
#   - Check and complete lig kern table and for special fonts
#   - add_lig_kern
#
####################################################################################################

""" This module handles TeX Font Metric.

The class :class:`PyDVI.Tfm` handles the font's metric.  To get a :class:`PyDVI.Tfm` instance for a
particular font use the static method :meth:`PyDVI.TfmParser.TfmParser.parse`.  For example use this
code for the font "cmr10"::

  tfm = TfmParser.parse('cmr10', '/usr/share/texmf/fonts/tfm/public/cm/cmr10.tfm')

The number of characters in the font can be obtained using the function :func:`len`::

  >>> len(tfm)
  128

Each character's metric is stored in a :class:`TfmChar` instance that can be accessed using the char
code as index on the :class:`Tfm` class instance.  For example to get the metric of the character
"A" use::

   tfm[ord('A')]

"""

####################################################################################################

__all__ = ['Tfm', 'TfmChar', 'TfmExtensibleChar', 'TfmKern', 'TfmLigature']

####################################################################################################

import string

####################################################################################################

from PyDVI.Tools.Logging import *

####################################################################################################

class TfmChar(object):

    """ This class encapsulates a TeX Font Metric for a Glyph.

    Public attributes:

       :attr:`char_code`

       :attr:`width`

       :attr:`height`

       :attr:`depth`

       :attr:`italic_correction`
    """

    #: List of the printable characters.
    printable = string.digits + string.letters + string.punctuation

    ##############################################

    def __init__(self,
                 tfm,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction,
                 lig_kern_program_index=None,
                 next_larger_char=None):

        self.tfm = tfm
        tfm[char_code] = self

        self.char_code = char_code
        self.width = width
        self.height = height
        self.depth = depth
        self.italic_correction = italic_correction

        self.lig_kern_program_index = lig_kern_program_index
        self.next_larger_char = next_larger_char

    ##############################################

    def scaled_width(self, scale_factor):

        """ Return the scaled width by *scale_factor*. """

        return int(self.width * scale_factor)

    ##############################################

    def scaled_height(self, scale_factor):

        """ Return the scaled height by *scale_factor*. """

        return int(self.height * scale_factor)

    ##############################################

    def scaled_depth(self, scale_factor):

        """ Return the scaled depth by *scale_factor*. """

        return int(self.depth * scale_factor)

    ##############################################

    def scaled_dimensions(self, scale_factor):

        """ Return the 3-tuple made of the scaled width, height and depth by *scale_factor*. """

        return [int(x * scale_factor) for x in self.width, self.height, self.depth]

    ##############################################

    def next_larger_tfm_char(self):

        """ Return the :class:`TfmChar` instance for the next larger char if it exists else return
        :obj:`None`."""

        if self.next_larger_char is not None:
            return self.tfm[self.next_larger_char]
        else:
            return None

    ##############################################

    def get_lig_kern_program(self):

        """ Get the ligature/kern program of the character. """

        if self.lig_kern_program_index is not None:
            return self.tfm.get_lig_kern_program(self.lig_kern_program_index)
        else:
            return None

    ##############################################

    def chr(self):

        """ Return the character string from its char code if it is printable. """

        char = chr(self.char_code)
        if char in self.printable:
            return char
        else:
            return self.char_code

    ##############################################

    def print_summary(self):

        string_format = '''TFM Char %u %s
 - width             %.3f
 - height            %.3f
 - depth             %.3f
 - italic correction %.3f
 - lig kern program index %s
 - next larger char       %s'''

        message = string_format % (self.char_code, self.chr(),
                                   self.width,
                                   self.height,
                                   self.depth,
                                   self.italic_correction,
                                   str(self.lig_kern_program_index),
                                   str(self.next_larger_char),
                                   )

        first_lig_kern = self.get_lig_kern_program()
        if first_lig_kern is not None:
            for lig_kern in first_lig_kern:
                message += '\n' + str(lig_kern)

        print_card(message)

####################################################################################################

class TfmExtensibleChar(TfmChar):

    """ This class encapsulates a TeX Font Metric for an extensible Glyph.

    Public attributes:

      :attr:`top`

      :attr:`mid`

      :attr:`bot`

      :attr:`rep`
     """

    ##############################################

    def __init__(self,
                 tfm,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction,
                 extensible_recipe,
                 lig_kern_program_index=None,
                 next_larger_char=None):

        super(TfmExtensibleChar, self).__init__(tfm,
                                                char_code,
                                                width,
                                                height,
                                                depth,
                                                italic_correction,
                                                lig_kern_program_index,
                                                next_larger_char)

        self.top, self.mid, self.bot, self.rep = extensible_recipe

####################################################################################################

class TfmLigKern(object):

    """ This classe serves of base class for ligature and kern program instruction.
    """

    ##############################################

    def __init__(self, tfm, index, stop, next_char):

        self.tfm = tfm
        self.stop = stop
        self.index = index
        self.next_char = next_char

        self.tfm.add_lig_kern(self)

    ##############################################

    def __iter__(self):

        """ Iterate of the ligature/kern program. """

        i = self.index
        while True:
            lig_kern = self.tfm.get_lig_kern_program(i)
            yield lig_kern
            if lig_kern.stop:
                break
            else:
                i += 1

####################################################################################################

class TfmKern(TfmLigKern):

    """ This class represents a Kerning Program Instruction.

    Public Attributes:

      :attr:`next_char`
        next character

      :attr:`kern`
        kerning value
    """

    ##############################################

    def __init__(self, tfm, index, stop, next_char, kern):

        super(TfmKern, self).__init__(tfm, index, stop, next_char)

        self.kern = kern

    ##############################################

    def __str__(self):

        return 'Kern char code %3u %s %0.6f' % (
            self.next_char,
            self.tfm[self.next_char].chr(),
            self.kern,
            )
    
####################################################################################################

class TfmLigature(TfmLigKern):

    """ This class represents a Ligature Program Instruction.

    Public Attributes:

      :attr:`next_char`
        next character

      :attr:`ligature_char_code`
        ligature character code

      :attr:`current_char_is_deleted`
        the current characters must be deleted of the stream

      :attr:`next_char_is_deleted`
        the next characters must be deleted of the stream

      :attr:`number_of_chars_to_pass_over`
        number of characters to pass over

    """

    ##############################################

    def __init__(self,
                 tfm,
                 index,
                 stop,
                 next_char,
                 ligature_char_code,
                 number_of_chars_to_pass_over,
                 current_char_is_deleted,
                 next_char_is_deleted):

        super(TfmLigature, self).__init__(tfm, index, stop, next_char)

        self.ligature_char_code = ligature_char_code
        self.number_of_chars_to_pass_over = number_of_chars_to_pass_over
        self.current_char_is_deleted = current_char_is_deleted
        self.next_char_is_deleted = next_char_is_deleted

    ##############################################

    def __str__(self):

        return 'Lig char code %3u %s ligature char code %3u' % (
            self.next_char,
            self.tfm[self.next_char].chr(),
            self.ligature_char_code,
            )
    
####################################################################################################

class Tfm(object):

    """ This class encapsulates a TeX Font Metric for a font.

    Public attributes:

      :attr:`font_name`
        font's name

      :attr:`filename`
        ".tfm" filename

      :attr:`smallest_character_code`
        smallest character code of the font

      :attr:`largest_character_code`
        largest character code of the font

      :attr:`checksum`
        checksum of the tfm file

      :attr:`design_font_size`
        design font size

      :attr:`character_coding_scheme`
        character coding scheme

      :attr:`family`
        font's family

      :attr:`slant`

      :attr:`spacing`

      :attr:`space_stretch`

      :attr:`space_shrink`

      :attr:`x_height`

      :attr:`quad`

      :attr:`extra_space`

    In addition for Math font, the following public attributes are available:

      :attr:`um1`

      :attr:`num2`

      :attr:`num3`

      :attr:`denom1`

      :attr:`denom2`

      :attr:`sup1`

      :attr:`sup2`

      :attr:`sup3`

      :attr:`sub1`

      :attr:`sub2`

      :attr:`supdrop`

      :attr:`subdrop`

      :attr:`delim1`

      :attr:`delim2`

      :attr:`axis_height`

      :attr:`default_rule_thickness`

      :attr:`big_op_spacing`

    The number of characters can be queried using :func:`len`. The :class:`TfmChar` instance for a
    character code *char_code* can be set or get using the operator [].
    """

    ##############################################

    def __init__(self,
                 font_name,
                 filename,
                 smallest_character_code,
                 largest_character_code,
                 checksum,
                 design_font_size,
                 character_coding_scheme,
                 family):

        self.font_name = font_name
        self.filename = filename
        self.smallest_character_code = smallest_character_code
        self.largest_character_code = largest_character_code
        self.checksum = checksum
        self.design_font_size = design_font_size
        self.character_coding_scheme = character_coding_scheme
        self.family = family

        self._lig_kerns = []
        self._chars = {}

    ##############################################

    def __setitem__(self, char_code, value):

        """ Set the :class:`TfmChar` instance for the character code *char_code*. """

        self._chars[char_code] = value

    ##############################################

    def __getitem__(self, char_code):

        """ Return the :class:`TfmChar` instance for the character code *char_code*. """

        return self._chars[char_code]

    ##############################################

    def __len__(self):

        """ Return the number of characters. """ 

        # return self.largest_character_code - self.smallest_character_code +1

        return len(self._chars)

    ##############################################

    def set_font_parameters(self, parameters):

        """ Set the font parameters. """

        (self.slant,
         self.spacing,
         self.space_stretch,
         self.space_shrink,
         self.x_height,
         self.quad,
         self.extra_space) = parameters

    ##############################################

    def set_math_symbols_parameters(self, parameters):
          
        """ Set the math symbols parameters. """

        (self.num1,
         self.num2,
         self.num3,
         self.denom1,
         self.denom2,
         self.sup1,
         self.sup2,
         self.sup3,
         self.sub1,
         self.sub2,
         self.supdrop,
         self.subdrop,
         self.delim1,
         self.delim2,
         self.axis_height) = parameters

    ##############################################

    def set_math_extension_parameters(self, parameters):

        """ Set the math extension parameters. """

        self.default_rule_thickness = parameters[0]
        self.big_op_spacing = parameters[1:]

    ##############################################

    def add_lig_kern(self, obj):

        """ Add a ligature/kern program *obj*. """

        self._lig_kerns.append(obj)

    ##############################################

    def get_lig_kern_program(self, i):

        """ Return the ligature/kern program at index *i*. """

        return self._lig_kerns[i]

    ##############################################

    def print_summary(self):

        string_format = '''TFM %s

 - Smallest character code in the font: %u 
 - Largest character code in the font:  %u 

 - Checksum: %u
 - Design Font Size: %f
 - Character coding scheme: "%s"
 - Family: "%s"

Font Parameters:
 - Slant: %f
 - Spacing: %f
 - Space Stretch: %f
 - Space Shrink: %f
 - X Height: %f
 - Quad: %f
 - Extra Space: %f'''

        message = string_format % (self.font_name,
                                   self.smallest_character_code,
                                   self.largest_character_code,
                                   self.checksum,
                                   self.design_font_size,
                                   self.character_coding_scheme,
                                   self.family,
                                   self.slant,
                                   self.spacing,
                                   self.space_stretch,
                                   self.space_shrink,
                                   self.x_height,
                                   self.quad,
                                   self.extra_space,
                                   )

        print_card(message)
        for char in self._chars.values():
            char.print_summary()

####################################################################################################
#
# End
#
####################################################################################################
