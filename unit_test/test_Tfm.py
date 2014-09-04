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
# - 20/11/2011 fabrice
#
####################################################################################################

####################################################################################################

import unittest

####################################################################################################

from PyDvi.Font.Encoding import *
from PyDvi.Font.Tfm import *
from PyDvi.Font.TfmParser import *
from PyDvi.Kpathsea import *

####################################################################################################

class TestTfm(unittest.TestCase):

    def test_cmr10(self):

        encoding_file = kpsewhich('ec', file_format='enc files')
        self.assertIsNotNone(encoding_file)
        encoding = Encoding(encoding_file)

        font_name = 'cmr10'
        tfm_file = kpsewhich(font_name, file_format='tfm')
        self.assertIsNotNone(tfm_file)
        print 'TFM file:', tfm_file

        tfm = TfmParser.parse(font_name, tfm_file)

        self.assertEqual(tfm.family, 'CMR')
        self.assertEqual(tfm.checksum, 011374260171) # tftopl output an octal representation
        self.assertEqual(tfm.design_font_size, 10)
        self.assertEqual(tfm.character_coding_scheme, 'TeX text')

        self.assertEqual(len(tfm), 128)

        self.assertAlmostEqual(tfm.slant, 0.0, places=6)
        self.assertAlmostEqual(tfm.spacing, 0.333334, places=6)
        self.assertAlmostEqual(tfm.space_stretch, 0.166667, places=6)
        self.assertAlmostEqual(tfm.space_shrink, 0.111112, places=6)
        self.assertAlmostEqual(tfm.x_height, 0.430555, places=6)
        self.assertAlmostEqual(tfm.quad, 1.000003, places=6)
        self.assertAlmostEqual(tfm.extra_space, 0.111112, places=6)

        tfm_char_j = tfm[ord('j')]
        # tfm_char_j = tfm[encoding.to_index('j')]
        self.assertAlmostEqual(tfm_char_j.width, 0.305557, places=6)
        self.assertAlmostEqual(tfm_char_j.height, 0.667859, places=6)
        self.assertAlmostEqual(tfm_char_j.depth, 0.194445, places=6)

        tfm_char_f = tfm[ord('f')]
        # tfm_char_f = tfm[encoding.to_index('f')]
        # tfm_char_f.print_summary()
        self.assertAlmostEqual(tfm_char_f.width, 0.305557, places=6)
        self.assertAlmostEqual(tfm_char_f.height, 0.694445, places=6)
        # self.assertAlmostEqual(tfm_char_f., 0.077779, places=6) # CHARIC
        lig_kern_it = list(tfm_char_f.get_lig_kern_program()) # Fixme
        self.assertEqual(lig_kern_it[0].next_char, ord('i'))
        self.assertEqual(lig_kern_it[0].ligature_char_code, 014)
        self.assertEqual(lig_kern_it[1].next_char, ord('f'))
        self.assertEqual(lig_kern_it[1].ligature_char_code, 013)
        self.assertEqual(lig_kern_it[2].next_char, ord('l'))
        self.assertEqual(lig_kern_it[2].ligature_char_code, 015)
        self.assertEqual(lig_kern_it[3].next_char, 047)
        self.assertAlmostEqual(lig_kern_it[3].kern, 0.077779, places=6)
        self.assertEqual(lig_kern_it[4].next_char, 077)
        self.assertAlmostEqual(lig_kern_it[4].kern, 0.077779, places=6)
        self.assertEqual(lig_kern_it[5].next_char, 041)
        self.assertAlmostEqual(lig_kern_it[5].kern, 0.077779, places=6)
        self.assertEqual(lig_kern_it[6].next_char, 051)
        self.assertAlmostEqual(lig_kern_it[6].kern, 0.077779, places=6)
        self.assertEqual(lig_kern_it[7].next_char, 0135)
        self.assertAlmostEqual(lig_kern_it[7].kern, 0.077779, places=6)

    def test_euex10(self):

        font_name = 'euex10'
        tfm_file = kpsewhich(font_name, file_format='tfm')
        self.assertIsNotNone(tfm_file)
        print 'TFM file:', tfm_file

        tfm = TfmParser.parse(font_name, tfm_file)

        self.assertEqual(tfm.family, 'EUEX V2.2')
        self.assertEqual(tfm.checksum, 014201660461) # tftopl output an octal representation
        self.assertEqual(tfm.design_font_size, 10)
        self.assertEqual(tfm.character_coding_scheme, 'euler substitutions only')

        self.assertAlmostEqual(tfm.slant, 0.0, places=6)
        self.assertAlmostEqual(tfm.spacing, 0.0, places=6)
        self.assertAlmostEqual(tfm.space_stretch, 0.0, places=6)
        self.assertAlmostEqual(tfm.space_shrink, 0.0, places=6)
        self.assertAlmostEqual(tfm.x_height, 0.430555, places=6)
        self.assertAlmostEqual(tfm.quad, 1.000003, places=6)
        self.assertAlmostEqual(tfm.extra_space, 0.0, places=6)
        
        self.assertAlmostEqual(tfm.default_rule_thickness, 0.039999, places=6)
        self.assertAlmostEqual(tfm.big_op_spacing[0], 0.111112, places=6)
        self.assertAlmostEqual(tfm.big_op_spacing[1], 0.166667, places=6)
        self.assertAlmostEqual(tfm.big_op_spacing[2], 0.2, places=6)
        self.assertAlmostEqual(tfm.big_op_spacing[3], 0.6, places=6)
        self.assertAlmostEqual(tfm.big_op_spacing[4], 0.1, places=6)

        tfm_char = tfm[010]
        self.assertAlmostEqual(tfm_char.width, 0.583336, places=6)
        self.assertAlmostEqual(tfm_char.height, 0.039999, places=6)
        self.assertAlmostEqual(tfm_char.depth, 1.160013, places=6)
        self.assertEqual(tfm_char.next_larger_char, 012)

        tfm_char = tfm[ord('8')]
        self.assertAlmostEqual(tfm_char.width, 0.888891, places=6)
        self.assertAlmostEqual(tfm_char.height, 0.0, places=6)
        self.assertAlmostEqual(tfm_char.depth, 0.900009, places=6)
        self.assertEqual(tfm_char.top, ord('8'))
        self.assertEqual(tfm_char.mid, 074)
        self.assertEqual(tfm_char.bot, 072)
        self.assertEqual(tfm_char.rep, 076)

####################################################################################################

# self.assertAlmostEqual(tfm.num1, , places=6)
# self.assertAlmostEqual(tfm.num2, , places=6)
# self.assertAlmostEqual(tfm.num3, , places=6)
# self.assertAlmostEqual(tfm.denom1, , places=6)
# self.assertAlmostEqual(tfm.denom2, , places=6)
# self.assertAlmostEqual(tfm.sup1, , places=6)
# self.assertAlmostEqual(tfm.sup2, , places=6)
# self.assertAlmostEqual(tfm.sup3, , places=6)
# self.assertAlmostEqual(tfm.sub1, , places=6)
# self.assertAlmostEqual(tfm.sub2, , places=6)
# self.assertAlmostEqual(tfm.supdrop, , places=6)
# self.assertAlmostEqual(tfm.subdrop, , places=6)
# self.assertAlmostEqual(tfm.delim1, , places=6)
# self.assertAlmostEqual(tfm.delim2, , places=6)
# self.assertAlmostEqual(tfm.axis_height, , places=6)
       
####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
