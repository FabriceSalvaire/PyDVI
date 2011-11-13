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
#  - 17/01/2010 fabrice
#   - TfmChar -> Char
#   - Check and complete lig kern table and for special fonts
#
#####################################################################################################

#####################################################################################################

__all__ = ['Tfm', 'TfmChar', 'TfmExtensibleChar', 'TfmKern', 'TfmLigature']

#####################################################################################################

import string

#####################################################################################################

from PyDVI.Tools.Logging import *

#####################################################################################################

class TfmChar(object):

    '''TeX Font Metric for a Glyph

    Public:
      - char_code
      - width
      - height
      - depth
      - italic_correction
    '''

    printable = string.digits + string.letters + string.punctuation

    ###############################################

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

        self.char_code = char_code
        self.width = width
        self.height = height
        self.depth = depth
        self.italic_correction = italic_correction

        self.lig_kern_program_index = lig_kern_program_index
        self.next_larger_char = next_larger_char

        self.tfm.add_char(self)

    ###############################################

    def get_scaled_width(self, scale_factor):

        return int(self.width * scale_factor)

    ###############################################

    def get_scaled_height(self, scale_factor):

        return int(self.height * scale_factor)

    ###############################################

    def get_scaled_depth(self, scale_factor):

        return int(self.depth * scale_factor)

    ###############################################

    def get_scaled_dimensions(self, scale_factor):

        return map(lambda x: int(x * scale_factor),
                   (self.width, self.height, self.depth))

    ###############################################

    def get_next_larger_char(self):

        if self.next_larger_char is not None:
            return self.tfm[self.next_larger_char]
        else:
            return None

    ###############################################

    def get_lig_kern_program(self):

        if self.lig_kern_program_index is not None:
            return self.tfm.get_lig_kern_program(self.lig_kern_program_index)
        else:
            return None

    ###############################################

    def chr(self):

        char = chr(self.char_code)
        
        if char not in self.printable:
            return self.char_code
        else:
            return char

    ###############################################

    def print_summary(self):

        message = '''TFM Char %u %s
 - width             %.3f
 - height            %.3f
 - depth             %.3f
 - italic correction %.3f
 - lig kern program index %s
 - next larger char       %s''' % (
            self.char_code, self.chr(),
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

#####################################################################################################

class TfmExtensibleChar(TfmChar):

    '''TeX Font Metric for an extensible Glyph

    Public:
     - top
     - mid
     - bot
     - rep
    '''

    ###############################################

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

#####################################################################################################

class TfmLigKern(object):

    ###############################################

    def __init__(self, tfm, index, stop, next_char):

        self.tfm = tfm
        self.stop = stop
        self.index = index
        self.next_char = next_char

        self.tfm.add_lig_kern(self)

    ###############################################

    def __iter__(self):

        i = self.index
        
        while True:
            
            lig_kern = self.tfm.lig_kerns[i]
            
            yield lig_kern
            
            if lig_kern.stop:
                break
            else:
                i += 1

#####################################################################################################

class TfmKern(TfmLigKern):

    '''Kerning

    Public:
      - kern
    '''

    ###############################################

    def __init__(self, tfm, index, stop, next_char, kern):

        super(TfmKern, self).__init__(tfm, index, stop, next_char)

        self.kern = kern

    ###############################################

    def __str__(self):

        return 'Kern char code %3u %s %.3f' % (
            self.next_char,
            self.tfm[self.next_char].chr(),
            self.kern,
            )
    
#####################################################################################################

class TfmLigature(TfmLigKern):

    '''Ligature
    '''

    ###############################################

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

    ###############################################

    def __str__(self):

        return 'Lig char code %3u %s ligature char code %3u' % (
            self.next_char,
            self.tfm[self.next_char].chr(),
            self.ligature_char_code,
            )
    
#####################################################################################################

class Tfm(object):

    ###############################################

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

        self.lig_kerns = []

        self.chars = {}

    ###############################################

    def __getitem__(self, char_code):

        return self.chars[char_code]

    ###############################################

    def __len__(self):

        # return self.largest_character_code - self.smallest_character_code +1

        return len(self.chars)

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

    def add_char(self, char):

        # __setitem__

        self.chars[char.char_code] = char

    ###############################################

    def add_lig_kern(self, obj):

        self.lig_kerns.append(obj)

    ###############################################

    def get_lig_kern_program(self, i):

        self.lig_kerns[i]

    ###############################################

    def print_summary(self):

        print_card('''TFM %s

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
 - Extra Space: %f''' % (
                self.font_name,
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
                ))

        for char in self.chars.values():
            char.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
