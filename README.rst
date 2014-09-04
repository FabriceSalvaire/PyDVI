===================
PyDvi V0.1.0
===================

PyDvi is a Python library that provides tools to read TeX DVI file, Packed Font and TeX Font Metric,
Font Map and Font Encoding. The library provides a DVI Machine base class hat can be plugged to a
TeX Daemon instance in order to render on-the-fly TeX inputs.

:Info: The home page of PyDvi is located at http://fabricesalvaire.github.com/PyDvi

Source Repository
-----------------

The PyDvi project is hosted at github
http://github.com/FabriceSalvaire/PyDvi

Requirements
------------

* Python 2.7
* PyQt 4.9
* Numpy

Building & Installing
---------------------

Download and unpack the source, then run the following commands in a terminal::

  python setup.py build
  python setup.py install

Running
-------

The program *gui/dvi-viewer* is a DVI Viewer demonstrator.

The program *gui/font-viewer* is a tool to display font glyph.

To run the unit tests use this shell command::

  for i in unit_test/*.py; do python $i; done

To run the test programs do::

  python test/test_dvi_machine.py tex-samples/text.cmr.latin1.dvi
  python test/test_encoding.py ec.enc
  python test/test_font_manager.py
  python test/test_font_map.py pdftex.map
  python test/test_pkfont.py cmr10
  python test/test_tex_daemon.py
  python test/test_tfm.py cmr10

To Go Further
-------------

:Warning: The development of PyDvi is on standby since several years now.

Some idea to go further:

* implement an OpenGL based viewer, actual Qt rendering is inefficient
* use Freetype to render the glyph, cf. http://code.google.com/p/freetype-gl and distance field
  rendering technique
* review the font manager
* review the DVI machine
* review everything
* try pypy

.. End
