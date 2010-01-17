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
#  - 00/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['Interval1D', 'Interval2D']

#####################################################################################################

import math

#####################################################################################################
    
class Interval1D(object):

    ###############################################
    
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Interval1D):
            self.inf = args[0].inf
            self.sup = args[0].sup
        else:
            self.inf = args[0]
            self.sup = args[1]

    ###############################################
    
    def __str__(self):
        return '[%i, %i]' % (self.inf, self.sup)

    ###############################################
    
    def print_object(self):
        print str(self)

    ###############################################

    def shift(self, dx):
        self.inf += dx
        self.sup += dx

    ###############################################

    def shift_inf_to_zero(self):
        return Interval1D(0, self.sup - self.inf)

    ###############################################

    def map_in(self, interval_reference):
        return Interval1D(self.inf - interval_reference.inf,
                          self.sup - interval_reference.inf)

    ###############################################

    def map_x_in(self, x):
        return x - self.inf

    ###############################################

    def unmap_x_in(self, x):
        return x + self.inf

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

    # i1 < i2
    def __lt__(i1, i2):
        return i1.sup < i2.inf

    ###############################################

    # i1 > i2
    def __gt__(i1, i2):
        return i1.inf > i2.sup

   ###############################################

    def intersect(self, i2):

        if self.inf == i2.inf:
            return True
        else:
            if self.inf < i2.inf:
                return   i2.inf <= self.sup
            else:
                return self.inf <=   i2.sup

    ###############################################

    def is_included_in(self, i2):
        # print '(%f <= %f and %f <= %f)' % (i2.inf, self.inf, self.sup, i2.sup)
        
        return i2.inf <= self.inf and self.sup <= i2.sup

    ###############################################

    def length(self):
        return self.sup - self.inf +1

    ###############################################

    def length_float(self):
        return self.sup - self.inf

    ###############################################

    def frange(self):
        return xrange(self.inf, self.sup +1)

#################################################################################

class Interval2D(object):

    ###############################################

    def __init__(self, x, y):

        # fixme

        if isinstance(x, list):
            self.x = Interval1D(x[0], x[1])
        elif isinstance(x, Interval1D):
            self.x = x
        else:
            self = None
            
        if isinstance(y, list):
            self.y = Interval1D(y[0], y[1])
        elif isinstance(y, Interval1D):
            self.y = y
        else:
            self = None

    ###############################################
    
    def __str__(self):
        return '[%i, %i]*[%i, %i]' % (self.x.inf, self.x.sup, self.y.inf, self.y.sup)

    ###############################################
    
    def print_object(self):
        print str(self)

    ###############################################

    def to_tuple(self):
        return(self.x.inf, self.x.sup, self.y.inf, self.y.sup)

    ###############################################

    def bounding_box(self):
        return(self.x.inf, self.y.inf, self.x.sup, self.y.sup)

    ###############################################

    def shift(self, dx, dy):
        self.x.shift(dx)
        self.y.shift(dy)

    ###############################################

    def shift_inf_to_zero(self):
        return Interval2D(self.x.shift_inf_to_zero(), self.y.shift_inf_to_zero())

    ###############################################

    def map_in(self, interval_reference):
        return Interval2D(self.x.map_in(interval_reference.x),
                          self.y.map_in(interval_reference.y))

    ###############################################

    def map_xy_in(self, x, y):
        return(self.x.map_x_in(x),
                self.y.map_x_in(y))

    ###############################################

    def unmap_xy_in(self, x, y):
        return(self.x.unmap_x_in(x),
                self.y.unmap_x_in(y))

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
        return(self.x.intersect(i2.x) and
                self.y.intersect(i2.y))

    ###############################################

    def is_included_in(self, i2):
        return(self.x.is_included_in(i2.x) and
                self.y.is_included_in(i2.y))

    ###############################################

    def size(self):
        return self.x.length(), self.y.length()

    ###############################################

    def area(self):
        return self.x.length_float() * self.y.length_float()

    ###############################################

    def diagonal(self):
        return math.sqrt((self.x.length_float())**2 + (self.y.length_float())**2)

#####################################################################################################
#
#                                               Test
#
#####################################################################################################

if __name__ == "__main__":

    i1 = Interval1D(1, 10)
    i2 = Interval1D(5, 15)

    i1.print_object()
    i2.print_object()

    i3 = i1 & i2

    i3.print_object()

    i4 = i1 | i2

    i4.print_object()

    ################################################

    #ii1 = Interval2D(x=Interval1D(100, 500), y=Interval1D(200, 600))
    ii1 = Interval2D([100, 500], [200, 600])
    ii2 = Interval2D(x=Interval1D(300, 800), y=Interval1D(400, 500))

    ii1.print_object()
    ii2.print_object()

    ii3 = ii1 & ii2

    ii3.print_object()

    ii4 = ii1 | ii2

    ii4.print_object()

    ii4.shift(100, 100)

    ii4.print_object()

    ii5 = ii4.shift_inf_to_zero()

    ii5.print_object()

    ################################################

    i1 = Interval1D(0, 1040 -1)
    i2 = Interval1D(i1)

    o = 1000

    i2.shift(o)

    i1.print_object()
    i2.print_object()

    i3 = i1 & i2

    i3.print_object()

    i4 = Interval1D(i3)

    i4.shift(-o)

    i4.print_object()

    i1 = Interval1D(100, 200)
    i2 = Interval1D(125, 160)

    i3 = i2.map_in(i1)

    print 'map_in'
    i1.print_object()
    i2.print_object()
    i3.print_object()

    ################################################

    i1 = Interval1D(0, 1040 -1)
    i2 = Interval1D(i1)

    o = -10

    i2.shift(o)

    i1.print_object()
    i2.print_object()

    i3 = i1 & i2

    i3.print_object()

    i4 = Interval1D(i3)

    i4.shift(-o)

    i4.print_object()

   ################################################

    i1 = Interval1D(0, 10)

    for i in i1.frange():
        print i

#####################################################################################################
#
# End
#
#####################################################################################################
