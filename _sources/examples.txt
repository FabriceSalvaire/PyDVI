.. -*- Mode: rst -*-

.. _examples-page:

.. include:: abbreviation.txt

==========
 Examples
==========

.. image:: /images/dvi-gl-viewer.scaled.png
  :scale: 50%	   
  :align: right

The program *gui/dvi-gl-viewer* is a DVI viewer demonstrator with a rendering accelerated by GPU
using the OpenGL API.

The program *gui/font-viewer* is a tool to display font glyph.

To run the unit tests use this shell command::

  for i in unit_test/*.py; do python $i; done

To run the test programs do::

  python test/test-dvi-machine tex-samples/text.cmr.latin1.dvi
  python test/test_encoding.py ec.enc
  python test/test_font_manager.py
  python test/test_font_map.py pdftex.map
  python test/test_pkfont.py cmr10
  python test/test_tex_daemon.py
  python test/test_tfm.py cmr10

.. End
