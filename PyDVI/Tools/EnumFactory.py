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
#  - 16/01/2010 fabrice
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['EnumFactory', 'ExplicitEnumFactory']

#####################################################################################################

class ReadOnlyMetaClass(type):

    ###############################################

    def __setattr__(self, name, value):

        raise NotImplementedError

#####################################################################################################

class EnumMetaClass(ReadOnlyMetaClass):

    ###############################################

    def __len__(self):

        return self._size

#####################################################################################################

class ExplicitEnumMetaClass(ReadOnlyMetaClass):

    ###############################################

    def __contains__(self, item):

        return item in self.constants

#################################################################################

def EnumFactory(enum_name, enum_tuple):

    dict = {}
    dict['_size'] = len(enum_tuple)
    for value, name in enumerate(enum_tuple):
        dict[name] = value

    return EnumMetaClass(enum_name, (), dict)

#################################################################################

def ExplicitEnumFactory(enum_name, enum_dict):

    dict = {}
    dict['constants'] = enum_dict.values()
    for name, value in enum_dict.items():
        dict[name] = value

    return ExplicitEnumMetaClass(enum_name, (), dict)

#####################################################################################################
#
# End
#
#####################################################################################################