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
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['Interval1D', 'Interval2D']

#####################################################################################################
    
class Interval1D(object):

    """This class implements an interval of rank 1.
    """

    ###############################################
    
    def __init__(self, *args):

        if len(args) == 1 and isinstance(args[0], Interval1D):
            self.inf = args[0].inf
            self.sup = args[0].sup
        elif isinstance(args, (list, tuple)):
            self.inf = args[0]
            self.sup = args[1]
        else:
            raise ValueError

    ###############################################
    
    def __str__(self):

        return '[%i, %i]' % (self.inf, self.sup)

    ###############################################
    
    def print_object(self):

        print str(self)

    ###############################################

    # Intersection

    def __and__(i1, i2):

        return Interval1D(max((i1.inf, i2.inf)), min((i1.sup, i2.sup)))

    def __iand__(self, i2):

        self.inf = max((self.inf, i2.inf))
        self.sup = min((self.sup, i2.sup))
        return self

    ###############################################

    # Union

    def __or__(i1, i2):

        return Interval1D(min((i1.inf, i2.inf)), max((i1.sup, i2.sup)))

    def __ior__(self, i2):

        self.inf = min((self.inf, i2.inf))
        self.sup = max((self.sup, i2.sup))
        return self

   ###############################################

    def intersect(self, i2):

        if self.inf == i2.inf:
            return True
        else:
            if self.inf < i2.inf:
                return i2.inf <= self.sup
            else:
                return self.inf <= i2.sup

    ###############################################

    def is_included_in(self, i2):
        
        return i2.inf <= self.inf and self.sup <= i2.sup

    ###############################################

    def length(self):

        return self.sup - self.inf

#################################################################################

class Interval2D(object):

    """This class implements an interval of rank 2.
    """

    ###############################################

    def __init__(self, x, y):

        self.x = self.__check_parameter(x)
        self.y = self.__check_parameter(y)

    ###############################################

    def __check_parameter(self, x):

        if isinstance(x, (list, tuple)):
            return Interval1D(x[0], x[1])
        elif isinstance(x, Interval1D):
            return x
        else:
            raise ValueError

    ###############################################
    
    def __str__(self):

        return '[%i, %i]*[%i, %i]' % (self.x.inf, self.x.sup, self.y.inf, self.y.sup)

    ###############################################
    
    def print_object(self):

        print str(self)

    ###############################################

    def bounding_box(self):

        return(self.x.inf, self.y.inf, self.x.sup, self.y.sup)

    ###############################################

    # Intersection

    def __and__(i1, i2):

        return Interval2D(i1.x & i2.x, i1.y & i2.y)

    def __iand__(self, i2):

        self.x &= i2.x
        self.y &= i2.y
        return self

    ###############################################

    # Union

    def __or__(i1, i2):

        return Interval2D(i1.x | i2.x, i1.y | i2.y)

    def __ior__(self, i2):

        self.x |= i2.x
        self.y |= i2.y
        return self

    ###############################################

    def intersect(self, i2):

        return self.x.intersect(i2.x) and self.y.intersect(i2.y)

    ###############################################

    def is_included_in(self, i2):

        return self.x.is_included_in(i2.x) and self.y.is_included_in(i2.y)

    ###############################################

    def size(self):

        return self.x.length(), self.y.length()

    ###############################################

    def area(self):

        return self.x.length() * self.y.length()

#####################################################################################################
#
# End
#
#####################################################################################################
