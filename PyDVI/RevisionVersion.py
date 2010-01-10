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
#  - 10/1/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['RevisionVersion']

#####################################################################################################

import re

#####################################################################################################

class RevisionVersion(object):

    scale = 10**3

    ###############################################

    def __init__(self, version):

        if isinstance(version, str):

            match = re.match('v([0-9]+)\.([0-9]+)\.([0-9]+)', version)

            if match is not None:
                (self.major,
                 self.minor,
                 self.revision) = [int(x) for x in match.groups()]
            else:
                raise NameError('Bad version string %s' % (version))
        
        elif isinstance(version, tuple):

            (self.major,
             self.minor,
             self.revision) = version

        else:
            raise NameError('parameter must be a string or a tuple')

        # Check the scale
        for x in self.major, self.minor, self.revision:
            if x >= self.scale:
                raise NameError('Version %s must be less than %u' % (str(self), self.scale))

    ###############################################

    def __eq__(a, b):

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 




#####################################################################################################

class RevisionVersion(object):

    scale = 10**3

    ###############################################

    def __init__(self, version):

        if isinstance(version, str):

            match = re.match('v([0-9]+)\.([0-9]+)\.([0-9]+)', version)

            if match is not None:
                (self.major,
                 self.minor,
                 self.revision) = [int(x) for x in match.groups()]
            else:
                raise NameError('Bad version string %s' % (version))
        
        elif isinstance(version, tuple):

            (self.major,
             self.minor,
             self.revision) = version

        else:
            raise NameError('parameter must be a string or a tuple')

        # Check the scale
        for x in self.major, self.minor, self.revision:
            if x >= self.scale:
                raise NameError('Version %s must be less than %u' % (str(self), self.scale))

    ###############################################

    def __eq__(a, b):

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 

    ###############################################

    def __ge__(a, b):

        return a.to_int() >= b.to_int()

    ###############################################

    def __gt__(a, b):

        return a.to_int() > b.to_int()

    ###############################################

    def __le__(a, b):

        return a.to_int() <= b.to_int()

    ###############################################

    def __lt__(a, b):

        return a.to_int() < b.to_int()
            
    ###############################################

    def __str__(self):

        return 'v%u.%u.%u' % (self.major, self.minor, self.revision)

    ###############################################

    def to_int(self):

        return (self.major * self.scale + self.minor) * self.scale + self.revision
        
    ###############################################

    def to_list(self):

        # Fixme: useful?

        return [self.major, self.minor, self.revision]

#####################################################################################################
#
# End
#
#####################################################################################################
