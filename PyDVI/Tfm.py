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

__all__ = ['Tfm', 'TfmChar']

#####################################################################################################

import string

#####################################################################################################

#####################################################################################################

class TfmChar(object):

    printable = string.digits + string.letters + string.punctuation

    ###############################################

    def __init__(self,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction):

        self.char_code = char_code
        self.width = width
        self.height = height
        self.depth = depth
        self.italic_correction = italic_correction

    ###############################################

    def chr(self):

        char = chr(self.char_code)
        
        if char not in self.printable:
            char = ''

        return char

    ###############################################

    def print_summary(self):

        print '''
Char %u %s
 - width             %.3f
 - height            %.3f
 - depth             %.3f
 - italic correction %.3f
''' % (self.char_code, self.chr(),
       self.width,
       self.height,
       self.depth,
       self.italic_correction,
       )

#####################################################################################################

class Tfm(object):

    ###############################################

    def __init__(self,
                 font_name,
                 smallest_character_code,
                 largest_character_code,
                 checksum,
                 design_font_size,
                 character_coding_scheme,
                 family):

        self.font_name = font_name
        self.smallest_character_code = smallest_character_code
        self.largest_character_code = largest_character_code
        self.checksum = checksum
        self.design_font_size = design_font_size
        self.character_coding_scheme = character_coding_scheme
        self.family = family

    ###############################################

    def set_font_parameters(self, parameters):

        (self.slant,
         self.spacing,
         self.space_stretch,
         self.space_shrink,
         self.x_height,
         self.quad,
         self.extra_space) = parameters

    ###############################################

    def set_math_symbols_parameters(self, parameters):
          
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

    ###############################################

    def set_math_extension_parameters(self, parameters):

        self.default_rule_thickness = parameters[0]
        self.big_op_spacing = parameters[1:]

    ###############################################

    def print_summary(self):

        print '''
TFM %s

 - Smallest character code in the font: %u 
 - Largest character code in the font: %u 

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
 - Extra Space: %f
''' % (self.font_name,
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
       self.extra_space)

#####################################################################################################
#
# End
#
#####################################################################################################
