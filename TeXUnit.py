#####################################################################################################

import fractions

#####################################################################################################

point_in_inch = fractions.Fraction(7227,100)
big_point_in_inch = 72
inch_in_mm = fractions.Fraction(254, 10)
cicero_in_didot = 12
didot_in_point = fractions.Fraction(1238, 1157)

point_in_mm = point_in_inch / inch_in_mm
mm_in_point = 1 / point_in_mm

#####################################################################################################

def mm2in(x):

    return x * float(inch_in_mm)

def in2mm(x):

    return x / float(inch_in_mm)

#####################################################################################################

def pt2in(x):

    return x * float(point_in_inch)

def in2pt(inch):

    return x / float(point_in_inch)

def pt2mm(x):

    return x * float(mm_in_point)

#####################################################################################################

def sp2pt(x):

    return x / float(2**16)

def sp2in(x):

    return pt2in(sp2pt(x))

def sp2mm(x):

    return pt2mm(sp2pt(x))

#####################################################################################################
#
# End
#
#####################################################################################################
