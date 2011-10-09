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
#  - 10/01/2010 fabrice
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['RevisionVersion']

#####################################################################################################

import re

#####################################################################################################

class RevisionVersion(object):

    """The RevisionVersion class permits to manage revision version of the form
    v(major).(minor).(revision).
    """

    # To compare version, we assume version < scale
    scale = 10**3

    ###############################################

    def __init__(self, version):

        """Create new RevisionVersion instance.
        
        Parameters
        ----------
        version : string or tuple of integers

        Examples
        --------
        >>> RevisionVersion('v0.1.2')
        >>> RevisionVersion((0,1,2))
        """

        if isinstance(version, str):
            version_string_pattern = 'v' + '\.'.join(['([0-9]+)']*3)
            match = re.match(version_string_pattern, version)
            if match is not None:
                (self.major, self.minor, self.revision) = [int(x) for x in match.groups()]
            else:
                raise ValueError('Bad version string %s' % (version))
        
        elif isinstance(version, tuple):
            for x in version:
                if ((not isinstance(x, int)) or x < 0):
                    raise ValueError('parameter must be positive integer')
            (self.major, self.minor, self.revision) = version

        else:
            raise ValueError('parameter must be a string or a tuple of integers')

        # Check the scale
        for x in self.major, self.minor, self.revision:
            if x >= self.scale:
                raise ValueError('Version %s must be less than %u' % (str(self), self.scale))

    ###############################################

    def __int__(self):

        return (self.major * self.scale + self.minor) * self.scale + self.revision

    ###############################################

    def __eq__(a, b):

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 

    ###############################################

    def __ge__(a, b):

        return int(a) >= int(b)

    ###############################################

    def __gt__(a, b):

        return int(a) > int(b)

    ###############################################

    def __le__(a, b):

        return int(a) <= int(b)

    ###############################################

    def __lt__(a, b):

        return int(a) < int(b)
            
    ###############################################

    def __str__(self):

        return 'v%u.%u.%u' % (self.major, self.minor, self.revision)

   ###############################################

    # Fixme: useful?

    def to_list(self):

        return [self.major, self.minor, self.revision]

#####################################################################################################
#
# End
#
#####################################################################################################
