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

__all__ = ['Tfm', 'TfmChar', 'TfmExtensibleChar', 'TfmKern', 'TfmLigature']

#####################################################################################################

import string

#####################################################################################################

#####################################################################################################

class TfmChar(object):

    printable = string.digits + string.letters + string.punctuation

    ###############################################

    def __init__(self,
                 tfm,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction,
                 lig_kern_program_index = None,
                 next_larger_char = None):

        self.tfm = tfm
        self.char_code = char_code
        self.width = width
        self.height = height
        self.depth = depth
        self.italic_correction = italic_correction
        self.lig_kern_program_index = lig_kern_program_index
        self.next_larger_char = next_larger_char

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
 - lig kern program index %s
 - next larger char       %s
''' % (self.char_code, self.chr(),
       self.width,
       self.height,
       self.depth,
       self.italic_correction,
       str(self.lig_kern_program_index),
       str(self.next_larger_char),
       )

        if self.lig_kern_program_index is not None:

            self.tfm.lig_kerns[self.lig_kern_program_index].print_summary()

#####################################################################################################

class TfmExtensibleChar(TfmChar):

    ###############################################

    def __init__(self,
                 tfm,
                 char_code,
                 width,
                 height,
                 depth,
                 italic_correction,
                 extensible_characters,
                 lig_kern_program_index = None,
                 next_larger_char = None):

        super(TfmExtensibleChar, self).__init__(tfm,
                                                char_code,
                                                width,
                                                height,
                                                depth,
                                                italic_correction,
                                                extensible_recipe,
                                                lig_kern_program_index,
                                                next_larger_char)

        self.top, self.mid, self.bot, self.rep = extensible_recipe

#####################################################################################################

class TfmKern(object):

    ###############################################

    def __init__(self, index, next_char, kern):

        self.index = index
        self.next_char = next_char
        self.kern = kern

    ###############################################

    def print_summary(self):

        print 'Kern index %u char code %u %.3f' % (self.index,
                                                   self.next_char,
                                                   self.kern)

#####################################################################################################

class TfmLigature(object):

    ###############################################

    def __init__(self,
                 index,
                 next_char,
                 ligature_char_code,
                 number_of_chars_to_pass_over,
                 current_char_is_deleted,
                 next_char_is_deleted):

        self.index = index
        self.next_char = next_char
        self.ligature_char_code = ligature_char_code
        self.number_of_chars_to_pass_over = number_of_chars_to_pass_over
        self.current_char_is_deleted = current_char_is_deleted
        self.next_char_is_deleted = next_char_is_deleted

    ###############################################

    def print_summary(self):

        print 'Lig index %u char code %u ligature char code %u' % (self.index,
                                                                   self.next_char,
                                                                   self.ligature_char_code)

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

        self.lig_kerns = []

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

    def add_kern_ligature(self, obj):

        self.lig_kerns.append(obj)

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
