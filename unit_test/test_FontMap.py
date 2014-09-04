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

from PyDvi.Font.FontMap import *
from PyDvi.Kpathsea import *

####################################################################################################

class TestFontMap(unittest.TestCase):

    def test(self):

        fontmap_name = 'pdftex'
        fontmap_file = kpsewhich(fontmap_name, file_format='map')
        self.assertIsNotNone(fontmap_file)
        print 'Fontmap file:', fontmap_file

        fontmap = FontMap(fontmap_file)
        fontmap_entry = fontmap['cmmi10']
        self.assertEqual(fontmap_entry.tex_name, 'cmmi10')
        self.assertEqual(fontmap_entry.ps_font_name, 'CMMI10')
        # self.assertEqual(fontmap_entry.ps_snippet, '.167 SlantFont')
        # self.assertEqual(fontmap_entry.effects, )
        # self.assertEqual(fontmap_entry.encoding, )
        self.assertEqual(fontmap_entry.pfb_filename, 'cmmi10.pfb')

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
