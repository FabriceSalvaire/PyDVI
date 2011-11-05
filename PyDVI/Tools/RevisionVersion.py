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
# - 31/10/2011 Fabrice
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['RevisionVersion']

#####################################################################################################

import re

#####################################################################################################

class RevisionVersion(object):

    """ This class implements a revision version of the form vx.y.z where x, y and z are the major,
    minor and revision number respectively.

    To compare two versions, it computes the integer: (x * scale + y) * scale + z. Thus x, y and z
    must be less than the scale.
    """

    #: default scale value
    scale = 10**6 

    ###############################################

    def __init__(self, version):

        """        
        *version*
          could be a version string or a sequence of three integers.

        Examples::

          RevisionVersion('v0.1.2')
          RevisionVersion((0,1,2))
          RevisionVersion([0,1,2])
          
        Two Instances can be compared using operator: ``==``, ``<``, ``>``, ``<=``, ``>=``.

        An instance can be formated using :meth:`str` function.
        """

        if isinstance(version, str):
            version_string_pattern = 'v' + '\.'.join(['([0-9]+)']*3)
            match = re.match(version_string_pattern, version)
            if match is not None:
                self.major, self.minor, self.revision = [int(x) for x in match.groups()]
            else:
                raise ValueError('Bad version string %s' % (version))
        
        else:
            self.major, self.minor, self.revision = [int(x) for x in version[:3]]

        # Check the values
        for x in self.major, self.minor, self.revision:
            if x < 0 or x >= self.scale:
                raise ValueError('For version %s, %u must be in the range [0,%u[' %
                                 (str(self), x, self.scale))
            
    ###############################################

    def __int__(self):

        """ Compute an integer from the revision numbering """

        return (self.major * self.scale + self.minor) * self.scale + self.revision

    ###############################################

    def __eq__(a, b):

        """ Test if Va == Vb """

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 

    ###############################################

    def __ge__(a, b):

        """ Test if Va >= Vb """

        return int(a) >= int(b)

    ###############################################

    def __gt__(a, b):

        """ Test if Va > Vb """

        return int(a) > int(b)

    ###############################################

    def __le__(a, b):

        """ Test if Va <= Vb """

        return int(a) <= int(b)

    ###############################################

    def __lt__(a, b):

        """ Test if Va < Vb """

        return int(a) < int(b)
            
    ###############################################

    def __str__(self):

        """ Format the version as vx.y.z """

        return 'v%u.%u.%u' % (self.major, self.minor, self.revision)

#####################################################################################################
#
# End
#
#####################################################################################################
