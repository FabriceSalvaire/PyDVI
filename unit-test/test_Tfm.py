#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2011 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
# - 20/11/2011 fabrice
#
#####################################################################################################

#####################################################################################################

import unittest

#####################################################################################################

from PyDVI.Kpathsea import *
from PyDVI.TfmParser import *
from PyDVI.Tfm import *

#####################################################################################################

class TestTfm(unittest.TestCase):

    def test(self):

        font_name = 'cmr10'
        tfm_file = kpsewhich(font_name, file_format='tfm')
        self.assertIsNotNone(tfm_file)
        print 'TFM file:', tfm_file

        tfm_parser = TfmParser() 
        tfm = tfm_parser.parse(font_name, tfm_file)

        self.assertEqual(tfm.family, 'CMR')
        # self.assertEqual(tfm.checksum, 11374260171)
        self.assertEqual(tfm.design_font_size, 10)
        self.assertEqual(tfm.character_coding_scheme, 'TeX text')

        self.assertAlmostEqual(tfm.slant, 0.0, places=6)
        self.assertAlmostEqual(tfm.spacing, 0.333334, places=6)
        self.assertAlmostEqual(tfm.space_stretch, 0.166667, places=6)
        self.assertAlmostEqual(tfm.space_shrink, 0.111112, places=6)
        self.assertAlmostEqual(tfm.x_height, 0.430555, places=6)
        self.assertAlmostEqual(tfm.quad, 1.000003, places=6)
        self.assertAlmostEqual(tfm.extra_space, 0.111112, places=6)

        # tfm_char = tfm[65]

#####################################################################################################

if __name__ == '__main__':

    unittest.main()

#####################################################################################################
#
# End
#
#####################################################################################################
