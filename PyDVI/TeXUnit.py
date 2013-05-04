####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
#  - 09/10/2010 Fabrice
#
####################################################################################################

"""This module provides functions to convert units used in the TeX world:

* **mm** stands for milimetre,
* **in** stands for inch which corresponds to 25.4 mm,
* **pt** stands for TeX point, there is 72.27 pt in one inch,
* **sp** stands for scale point, there is 2**16 sp in one pt,
* **dpi** stands for dot per inch.

The DVI format uses the measure 100 nm as base unit. A scaled point is defined as a fraction:

* num = 2.54 * 1e7 = 25400000
* den = 7227 * 2**16 = 473628672
* 1 sp = num/den = 5.4 nm

For a resolution of 1200 dpi, a pixel measures 21 um.
"""

####################################################################################################

__all__ = ['dpi2mm',
           'in2mm', 'in2pt', 'in2sp',
           'mm2in',
           'pt2in', 'pt2mm', 'pt2sp',
           'sp2in', 'sp2mm', 'sp2pt', 'sp2dpi',
           ]

####################################################################################################

import fractions

####################################################################################################

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
sp_in_pt_f = float(scaled_point_in_point)

####################################################################################################

def mm2in(x):
    """Convert mm to in"""
    return x * inch_in_mm_f

def in2mm(x):
    """Convert in to mm"""
    return x * mm_in_inch_f

def dpi2mm(x):
    """Convert dpi to mm"""
    return mm_in_inch_f / x

####################################################################################################

def in2pt(x):
    """Convert in to pt"""
    return x * point_in_inch_f

def pt2in(x):
    """Convert in to pt"""
    return x * inch_in_point_f

def pt2mm(x):
    """Convert pt to mm"""
    return x * mm_in_point_f

####################################################################################################

def sp2pt(x):
    """Convert sp to pt"""
    return x * pt_in_sp_f

def sp2in(x):
    """Convert sp to in"""
    return pt2in(sp2pt(x))

def sp2mm(x):
    """Convert sp to mm"""
    return pt2mm(sp2pt(x))

def sp2dpi(x):
    """Convert sp to dpi"""
    return in2pt(sp2pt(x))

def pt2sp(x):
    """Convert pt to sp"""
    return x * sp_in_pt_f

def in2sp(x):
    """Convert in to sp"""
    return pt2sp(in2pt(x))

####################################################################################################
#
# End
#
####################################################################################################
