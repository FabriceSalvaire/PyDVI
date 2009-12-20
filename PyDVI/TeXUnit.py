#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['in2mm', 'in2pt', 'dpi2mm', 'mm2in', 'pt2in', 'pt2mm', 'sp2in', 'sp2mm', 'sp2pt', 'sp2dpi']

#####################################################################################################

import fractions

#####################################################################################################

#
# 7227 TeX points in 254 cm
#
# 2**16 scaled points (sp) in a point
#
# DVI use 1e-7 m unit
# 
#  num = 254e-2 * 1e7 =  25400000
#  den = 7227 * 2**16 = 473628672
#  1 sp = num/den = 5.4 nm
#  @ 1200 dpi: 1 pt = 21 um
#  

# 1 in = 72 bp
big_point_in_inch = 72
# 1 cc = 12 dd
didot_in_cicero = 12
# 1157 dd = 1238 pt
didot_in_point = fractions.Fraction(1157, 1238)
# 1 in = 25.4 mm
mm_in_inch = fractions.Fraction(254, 10)
# 1 in = 72.27 pt
point_in_inch = fractions.Fraction(7227, 100)
# 1 pt = 2**16 sp
scaled_point_in_point = 2**16

inch_in_mm = 1 / mm_in_inch
point_in_mm = point_in_inch * inch_in_mm
inch_in_point = 1 / point_in_inch
mm_in_point = 1 / point_in_mm
pt_in_sp = fractions.Fraction(1, scaled_point_in_point)

inch_in_mm_f = float(inch_in_mm)
inch_in_point_f = float(inch_in_point)
mm_in_inch_f = float(mm_in_inch)
mm_in_point_f = float(mm_in_point)
point_in_inch_f = float(point_in_inch)
pt_in_sp_f = float(pt_in_sp)

#####################################################################################################

def mm2in(x):

    return x * inch_in_mm_f

def in2mm(x):

    return x * mm_in_inch_f

def dpi2mm(x):

    return mm_in_inch_f / x

#####################################################################################################

def in2pt(x):

    return x * point_in_inch_f

def pt2in(x):

    return x * inch_in_point_f

def pt2mm(x):

    return x * mm_in_point_f

#####################################################################################################

def sp2pt(x):

    return x * pt_in_sp_f

def sp2in(x):

    return pt2in(sp2pt(x))

def sp2mm(x):

    return pt2mm(sp2pt(x))

def sp2dpi(x):

    return in2pt(sp2pt(x))

#####################################################################################################
#
# End
#
#####################################################################################################
