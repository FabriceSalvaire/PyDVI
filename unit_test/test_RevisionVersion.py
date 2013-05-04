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
#  - 09/10/2011 fabrice
#
####################################################################################################

####################################################################################################

import unittest

####################################################################################################

from PyDVI.Tools.RevisionVersion import *

####################################################################################################

class TestRevisionVersion(unittest.TestCase):

    def test(self):

        version_tuple = (1,2,3)
        version_string = 'v' + '.'.join([str(x) for x in version_tuple])

        version = RevisionVersion(version_tuple)
        self.assertEqual(version, RevisionVersion(version_string))
        self.assertEqual(str(version), version_string)

        # Only test >=
        self.assertTrue(RevisionVersion((1,2,3)) >= version)
        self.assertTrue(RevisionVersion((1,2,4)) >= version)
        self.assertTrue(RevisionVersion((1,3,4)) >= version)
        self.assertTrue(RevisionVersion((2,3,4)) >= version)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################
