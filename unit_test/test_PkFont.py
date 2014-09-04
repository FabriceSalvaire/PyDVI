####################################################################################################
#
# PyDvi - A Python Library to Process DVI Stream.
# Copyright (C) 2011 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
# - 01/12/2011 fabrice
#
####################################################################################################

####################################################################################################

import unittest

####################################################################################################

from PyDvi.Font.PkFont import PkFont
from PyDvi.Kpathsea import kpsewhich
from PyDvi.TeXUnit import *
from PyDvi.Tools.Stream import to_fix_word

####################################################################################################

class TestPkFont(unittest.TestCase):

    def test_cmr10(self):

        font_name = 'cmr10'
        pk_file = kpsewhich(font_name, file_format='pk')
        self.assertIsNotNone(pk_file)

        pk_font = PkFont(font_manager=None, font_id=0, name=font_name)

        comment_example = 'METAFONT output 2011.11.25:2115'
        self.assertEqual(len(pk_font.comment), len(comment_example))
        self.assertEqual(pk_font.checksum, 1274110073)
        self.assertEqual(pk_font.design_font_size, to_fix_word(10485760))
        self.assertEqual(pk_font.horizontal_dpi, sp2dpi(544093))
        self.assertEqual(pk_font.vertical_dpi, sp2dpi(544093))
       
        glyph = pk_font[65]
        self.assertEqual(glyph.char_code, 65)
        self.assertEqual(glyph.width, 55)
        self.assertEqual(glyph.height, 60)
        self.assertEqual(glyph.dyn_f, 10)
        self.assertEqual(glyph.tfm, to_fix_word(786434))
        self.assertEqual(glyph.dx, sp2pt(4063232))
        self.assertEqual(glyph.horizontal_offset, -3)
        self.assertEqual(glyph.vertical_offset, 59)
        glyph.print_summary()
        glyph.print_glyph()
        count_list = '(26)[2]3(51)[2]5(49)[2]7(47)[2]9(45)[1]2(1)8(43)3(1)9(42)[1]2(3)8(41)3(3)9(40)[1]2(5)8(39)3(5)9(38)[1]2(7)8(37)3(7)9(36)[1]2(9)8(35)3(9)9(34)[1]2(11)8(33)2(12)9(32)[1]2(13)8(31)2(14)9(30)[1]2(15)8(29)2(16)9(28)[1]2(17)8(27)2(18)9(26)[1]29(25)31(24)[1]2(21)8(23)[2]2(23)8(21)[2]2(25)8(19)[1]2(27)8(17)3(27)8(17)3(28)8(15)4(28)8(14)6(27)9(11)10(23)12(6)[2]17(15)23'
        print '\n', count_list
        self.assertEqual(glyph.count_list(), count_list)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
