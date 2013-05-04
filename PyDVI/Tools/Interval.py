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
#  - 13/05/2010 fabrice
#
####################################################################################################

####################################################################################################

__all__ = ['Interval', 'IntervalInt', 'Interval2D', 'IntervalInt2D']

####################################################################################################

from PyDVI.Tools.FuncTools import middle

####################################################################################################

empty_interval_string = '[empty]'

####################################################################################################
    
class Interval(object):

    """ One-dimension Interval
    """

    ##############################################

    # Fixme: better name than array ?
    
    def __init__(self, *args):

        """ Initialise an interval

        * Interval(inf, sup)
        * else args must support the __getitem__ interface, e.g.:

         * Interval((inf, sup))
         * Interval([inf, sup])
         * Interval(interval_instance)
        """

        array = self._check_arguments(args)

        self.inf = array[0]
        self.sup = array[1]

        if self.inf > self.sup: # None > None = False
            raise ValueError("inf <= sup condition is false [%u, %u]" % (self.inf, self.sup))

    ##############################################
    
    def _check_arguments(self, args):

        size = len(args)
        if size == 1:
            array = args[0]
        elif size == 2:
            array = args
        else:
            raise ValueError("Args size > 2")

        return array

    ##############################################

    def copy(self):

        """ Return a clone of the interval
        """

        return self.__class__(self.inf, self.sup)

    ##############################################
    
    def __getitem__(self, index):

        if isinstance(index, slice):
            if index.start is None:
                lower = 0
            else:
                lower = index.start

            if index.stop is None:
                upper = 1
            else:
                upper = index.stop -1

            if lower == 0 and upper == 1:
                return self.inf, self.sup
            elif lower == 0 and upper == 0: 
                return self.inf
            elif lower == 1 and upper == 1: 
                return self.sup
            else:
                raise IndexError("Wrong slice")

        elif index == 0:
            return self.inf
        elif index == 1:
            return self.sup
        else:
            raise IndexError("Index is out of range")

    ##############################################
    
    def __repr__(self):

        return str(self.__class__) + ' ' + str(self)

    ##############################################
    
    def __str__(self):

        if self.is_empty():
            return empty_interval_string
        else:
            return '[%f, %f]' % (self.inf, self.sup)

    ##############################################
    
    def print_object(self):

        """ Print the interval
        """

        print str(self)

    ##############################################

    def is_empty(self):

        return self.inf is None and self.sup is None

    ##############################################

    @staticmethod
    def _intersection(i1, i2):

        if i1.intersect(i2):
            return (max((i1.inf, i2.inf)),
                    min((i1.sup, i2.sup)))
        else:
            return None, None

    def __and__(i1, i2):

        """ Return the intersection of i1 and i2
        """

        return i1.__class__(i1._intersection(i1, i2))

    def __iand__(self, i2):

        """ Update the interval with its intersection with i2
        """

        self.inf, self.sup = self._intersection(self, i2)
        return self

    ##############################################

    @staticmethod
    def _union(i1, i2):

        return (min((i1.inf, i2.inf)),
                max((i1.sup, i2.sup)))

    def __or__(i1, i2):

        """ Return the union of i1 and i2
        """

        return i1.__class__(i1._union(i1, i2))

    def __ior__(self, i2):

        """ Update the interval with its union with i2
        """

        self.inf, self.sup = self._union(self, i2)
        return self

    ##############################################

    def __eq__(i1, i2):

        """ Equality test
        """

        return i1.inf == i2.inf and i1.sup == i2.sup

    ##############################################

    def __lt__(i1, i2):

        """ Test if i1.sup < i2.inf
        """

        return i1.sup < i2.inf

    ##############################################

    def __gt__(i1, i2):

        """ Test if i1.inf > i2.sup
        """

        return i1.inf > i2.sup

    ##############################################

    def __iadd__(self, dx):

        """ Shift the interval of dx
        """

        self.inf += dx
        self.sup += dx
        return self

    ##############################################

    def __add__(self, dx):

        """ Construct a new interval shifted of dx
        """

        return self.__class__((self.inf + dx,
                               self.sup + dx))

    ##############################################

    def __mul__(self, scale):

        """ Construct a new interval scaled by scale
        """

        return self.__class__((self.inf * scale,
                               self.sup * scale))

    ##############################################

    def __isub__(self, dx):

        """ Shift the interval of -dx
        """

        self.inf -= dx
        self.sup -= dx
        return self

    ##############################################

    def __sub__(self, dx):


        """ Construct a new interval shifted of -dx
        """

        return self.__class__((self.inf - dx,
                               self.sup - dx))

   ###############################################

    def intersect(i1, i2):

        """ Does the interval intersect with i2?
        """

        return ((i1.inf <= i2.sup and i2.inf <= i1.sup) or
                (i2.inf <= i1.sup and i1.inf <= i2.sup))

    ##############################################

    def __contains__(self, x):

        """ Is *x* in the interval?
        """

        return self.inf <= x and x <= self.sup
                
    ##############################################

    def is_included_in(i1, i2):

        """ Is the interval included in i1?
        """

        # print '(%f <= %f and %f <= %f)' % (i2.inf, i1.inf, i1.sup, i2.sup)
        
        return i2.inf <= i1.inf and i1.sup <= i2.sup

    ##############################################

    # Fixme: length -> size ?
  
    def length(self):

        """ Return sup - inf
        """

        return self.sup - self.inf

    ##############################################

    def zero_length(self):

        """ Return sup == inf
        """

        return self.sup == self.inf

    ##############################################

    def middle(self):

        """ Return interval middle
        """

        return middle(self.inf, self.sup)

    ##############################################

    def enlarge(self, dx):

        """ Enlarge the interval of dx
        """

        self.inf -= dx
        self.sup += dx

####################################################################################################
    
class IntervalInt(Interval):

    """ One-dimension Integer Interval
    """

    ##############################################

    # Fixme: better name than array ?
    
    def __init__(self, *args):

        """ Initialise an interval

        array must support the __getitem__ interface
        """

        array = self._check_arguments(args)

        if None not in array:
            array = [int(x) for x in array[:2]] # Fixme: rint ?
        # Fixme: else:

        super(IntervalInt, self).__init__(array)

    ##############################################
    
    def __str__(self):

        if self.is_empty():
            return empty_interval_string
        else:
            return '[%i, %i]' % (self.inf, self.sup)
        
    ##############################################
  
    def length(self):

        """ Return sup - inf +1
        """

        return self.sup - self.inf +1

#################################################################################

class Interval2D(object):

    """ Two-dimension Interval
    """

    ##############################################

    def __init__(self, x, y):

        """ Initialise a 2D interval

        x and y must support the __getitem__ interface
        """

        self.x = Interval(x)
        self.y = Interval(y)

    ##############################################

    def copy(self):

        """ Return a clone of the interval
        """

        return self.__class__(self.x, self.y)

    ##############################################
    
    def __setitem__(self, index, interval):

        if index == 0:
            self.x = interval
        elif index == 1:
            self.y = interval
        else:
            raise IndexError("Index is out of range")

    ##############################################
    
    def __getitem__(self, index):

        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index is out of range")

    ##############################################

    def __str__(self):

        return str(self.x) + '*' + str(self.y)

    ##############################################
    
    def __repr__(self):

        return str(self.__class__) + ' ' + str(self)

    ##############################################

    def print_object(self):

        """ Print the interval
        """

        print str(self)

    ##############################################

    def is_empty(self):

        return self.x.is_empty() or self.y.is_empty()

    ##############################################

    def __and__(i1, i2):

        """ Return the intersection of i1 and i2
        """

        return i1.__class__(i1.x & i2.x,
                            i1.y & i2.y)

    def __iand__(self, i2):

        """ Update the interval with its intersection with i2
        """

        self.x &= i2.x
        self.y &= i2.y
        return self

    ##############################################

    # Union

    def __or__(i1, i2):

        """ Return the union of i1 and i2
        """

        return i1.__class__(i1.x | i2.x,
                            i1.y | i2.y)

    def __ior__(self, i2):

        """ Update the interval with its union with i2
        """

        self.x |= i2.x
        self.y |= i2.y
        return self

    ##############################################

    def __eq__(i1, i2):

        """ Equality test
        """

        return i1.x == i2.x and i1.y == i2.y

    ##############################################

    def __iadd__(self, dxy):

        """ Shift the interval of *dxy*.
        """

        self.x += dx
        self.y += dy
        return self

    ##############################################

    def __add__(self, dxy):

        """ Construct a new interval shifted by *dxy*.
        """

        return self.__class__(self.x + dxy[0], self.y  + dxy[1])

    ##############################################

    def __imul__(self, scale):

        """ Scale the interval by *scale*.
        """

        self.x += scale
        self.y += scale
        return self

    ##############################################

    def __mul__(self, scale):

        """ Construct a new interval scaled by scale
        """

        return self.__class__(self.x * scale, self.y * scale)

    ##############################################

    def intersect(self, i2):

        """ Does the interval intersect with i2?
        """

        return (self.x.intersect(i2.x) and
                self.y.intersect(i2.y))

    ##############################################

    def is_included_in(self, i2):

        """ Is the interval included in i2?
        """

        return (self.x.is_included_in(i2.x) and
                self.y.is_included_in(i2.y))

    ##############################################

    def size(self):

        """ Return the horizontal and vertical size 
        """

        return self.x.length(), self.y.length()

    ##############################################

    def area(self):

        """ Return the area
        """

        return self.x.length() * self.y.length()

    ##############################################

    def bounding_box(self):

        """ Return the corresponding bounding box (x.inf, y.inf, x.sup, y.sup)
        """

        return (self.x.inf, self.y.inf,
                self.x.sup, self.y.sup)

    ##############################################

    def middle(self):

        """ Return interval middle
        """

        return self.x.middle(), self.y.middle()

    ##############################################

    def enlarge(self, dx):

        """ Enlarge the interval of dx
        """

        self.x.enlarge(dx)
        self.y.enlarge(dx)

####################################################################################################
    
class IntervalInt2D(Interval2D):

    """ Two-dimension Integer Interval
    """

    ##############################################

    def __init__(self, x, y):

        """ Initialise a 2D Integer interval

        x and y must support the __getitem__ interface
        """

        self.x = IntervalInt(x)
        self.y = IntervalInt(y)

####################################################################################################
#
# End
#
####################################################################################################
