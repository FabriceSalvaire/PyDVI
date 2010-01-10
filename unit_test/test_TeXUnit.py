#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################

import unittest

#####################################################################################################

from PyDVI.TeXUnit import *

#####################################################################################################

class TestTeXUnit(unittest.TestCase):

    def test(self):

        self.assertAlmostEqual(in2mm(10), 254)
        self.assertAlmostEqual(mm2in(in2mm(1)), 1)

        point_in_inch = 72.27

        self.assertAlmostEqual(pt2in(point_in_inch), 1)
        self.assertAlmostEqual(pt2mm(point_in_inch), in2mm(1))

        self.assertAlmostEqual(in2pt(pt2in(1)), 1)

        scaled_point_in_point = 2**16

        self.assertAlmostEqual(sp2pt(scaled_point_in_point), 1)
        self.assertAlmostEqual(sp2in(scaled_point_in_point), pt2in(1))
        self.assertAlmostEqual(sp2mm(scaled_point_in_point), pt2mm(1))

#####################################################################################################

if __name__ == '__main__':

    unittest.main()

#####################################################################################################
#
# End
#
#####################################################################################################
