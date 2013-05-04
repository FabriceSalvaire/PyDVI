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
from PyDVI.Encoding import *

#####################################################################################################

class TestEncoding(unittest.TestCase):

    def test(self):

        encoding_file = kpsewhich('ec', file_format='enc files')
        self.assertIsNotNone(encoding_file)
        print 'Encoding file:', encoding_file

        encoding = Encoding(encoding_file)
        self.assertEqual(len(encoding), 256)
        self.assertEqual(encoding.to_name(0xA0), 'abreve')
        self.assertEqual(encoding[0xA0], 'abreve')
        self.assertEqual(encoding.to_index('abreve'), 0xA0)
        self.assertEqual(encoding['abreve'], 0xA0)

#####################################################################################################

if __name__ == '__main__':

    unittest.main()

#####################################################################################################
#
# End
#
#####################################################################################################
