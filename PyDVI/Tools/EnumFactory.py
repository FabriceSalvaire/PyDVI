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
# - 27/11/2011 fabrice
#   - check metaclass protocol
#
####################################################################################################

""" This module provides an implementation for enumerate.

The enum factory :func:`EnumFactory` builds a enumerate from a list of names and assigns to these
constants a value from 0 to ``N-1``, where ``N`` is the number of constants::

  enum1 = EnumFactory('Enum1', ('cst1', 'cst2'))
   
then we can get a constant's value with::
     
  enum1.cst1

and the number of constants using::

  len(enum1)

The enum factory :func:`ExplicitEnumFactory` permits to specify the values of the constants::
        
  enum2 = ExplicitEnumFactory('Enum2', {'cst1':1, 'cst2':3})

We can test if a value is in the enum using::

  constant_value in enum2

"""

####################################################################################################

__all__ = ['EnumFactory', 'ExplicitEnumFactory']

####################################################################################################

class ReadOnlyMetaClass(type):

    """ This meta class implements a class where the attributes are read only. """

    ##############################################

    def __setattr__(self, name, value):

        raise NotImplementedError

####################################################################################################

class EnumMetaClass(ReadOnlyMetaClass):

    """ This meta class implements the function :func:`len`. """

    ##############################################

    def __len__(self):

        return self._size

####################################################################################################

class ExplicitEnumMetaClass(ReadOnlyMetaClass):

    """ This meta class implements the operator ``in``. """

    ##############################################

    def __contains__(self, item):

        return item in self.constants

#################################################################################

def EnumFactory(cls_name, constant_names):

    """ Return an :class:`EnumMetaClass` instance, where *cls_name* is the class name and
    *constant_names* is an iterable of constant's names.
    """

    dict_ = {}
    dict_['_size'] = len(constant_names)
    for index, name in enumerate(constant_names):
        dict_[str(name)] = index

    return EnumMetaClass(cls_name, (), dict_)

#################################################################################

def ExplicitEnumFactory(cls_name, constant_dict):

    """ Return an :class:`ExplicitEnumMetaClass` instance, where *cls_name* is the class name and
    *constant_dict* is a dict of constant's names and their values.
    """

    dict_ = {}
    dict_['constants'] = constant_dict.values()
    for name, value in constant_dict.items():
        dict_[name] = value

    return ExplicitEnumMetaClass(cls_name, (), dict_)

####################################################################################################
#
# End
#
####################################################################################################
