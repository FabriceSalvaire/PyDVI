==============
 Font Modules
==============

LaTeX uses the following types of font files:

 * .fd - font definition. Used to define a family of fonts.
 * .mf - metafont files. It defines the font shape.
 * .pk - packet font. It is a device dependent bitmap font.
 * .pl - property list. This is a human readable version of a tex font metric file.
 * .tfm - tex font metric. It describes the font metric and is completely
   analogous to the .afm files used by Type 1 fonts.
 * .vf - virtual font.
 * .vpl - virtual property list. Human readable version of a virtual font file.

A Packed Font file can be generated from the Metafont source files using the command :cmd:`mktexpk`,
for example::

  mktexpk --mfmode nextscrn --bdpi 100 --dpi 100 cmr10

will generate the *.pk* file for the cmr10 font at the resolution of 100 dpi. The Metafont mode
*nextscrn*, what stands for *Next Screen*, as a resolution of 100 dpi what is closed to the typical
LCD screen resolution.  The Metafont modes are defined in the file :file:`modes.mf`.  Also the TeX
Font Metric file can be generated using the :cmd:`mktextfm`, for example::

  mktextfm cmr10

will generate the *.tfm* file for the cmr10 font.  The locations of the generated files can be
rerieved using the command :cmd:`kpsewhich` from the Kpathsea library::

  kpsewhich cmr10.tfm
  kpsewhich -mode nextscrn -dpi 100 cmr10.pk

Moreover the required file can be generated on the fly using the option *-mktex*::

  kpsewhich --mktex=tfm cmr12.tfm
  kpsewhich -mode nextscrn -dpi 100 -mktex=pk cmr12.pk

The content of *.pk* and *.tfm* files can be printed on the console using the command :cmd:`pktype`
and :cmd:`tftopl`, respectively.

.. vftovp

*****************
 :mod:`Encoding`
*****************

.. automodule:: PyDVI.Encoding
   :members:

****************
 :mod:`FontMap`
****************

.. automodule:: PyDVI.FontMap
   :members:

******************
 :mod:`TfmParser`
******************

.. automodule:: PyDVI.TfmParser
   :members:

************
 :mod:`Tfm`
************

.. automodule:: PyDVI.Tfm
   :members:

.. End
