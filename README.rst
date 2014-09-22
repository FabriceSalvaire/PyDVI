.. -*- Mode: rst -*-

.. -*- Mode: rst -*-

..
   |PyDviUrl|
   |PyDviHomePage|_
   |PyDviDoc|_
   |PyDvi@github|_
   |PyDvi@readthedocs|_
   |PyDvi@readthedocs-badge|
   |PyDvi@pypi|_

.. |ohloh| image:: https://www.openhub.net/accounts/230426/widgets/account_tiny.gif
   :target: https://www.openhub.net/accounts/fabricesalvaire
   :alt: Fabrice Salvaire's Ohloh profile
   :height: 15px
   :width:  80px

.. |PyDviUrl| replace:: http://fabricesalvaire.github.io/PyDVI

.. |PyDviHomePage| replace:: PyDvi Home Page
.. _PyDviHomePage: http://fabricesalvaire.github.io/PyDVI

.. |PyDviDoc| replace:: PyDvi Documentation
.. _PyDviDoc: http://pydvi.readthedocs.org/en/latest

.. |PyDvi@readthedocs-badge| image:: https://readthedocs.org/projects/pydvi/badge/?version=latest
   :target: http://pydvi.readthedocs.org/en/latest

.. |PyDvi@github| replace:: https://github.com/FabriceSalvaire/PyDVI
.. .. _PyDvi@github: https://github.com/FabriceSalvaire/PyDVI

.. |PyDvi@readthedocs| replace:: http://pydvi.readthedocs.org
.. .. _PyDvi@readthedocs: http://pydvi.readthedocs.org

.. |PyDvi@pypi| replace:: https://pypi.python.org/pypi/PyDVI
.. .. _PyDvi@pypi: https://pypi.python.org/pypi/PyDVI

.. |Build Status| image:: https://travis-ci.org/FabriceSalvaire/PyDVI.svg?branch=master
   :target: https://travis-ci.org/FabriceSalvaire/PyDVI
   :alt: PyDvi build status @travis-ci.org

.. End
.. -*- Mode: rst -*-

.. |Python| replace:: Python
.. _Python: http://python.org

.. |PyPI| replace:: PyPI
.. _PyPI: https://pypi.python.org/pypi

.. |Numpy| replace:: Numpy
.. _Numpy: http://www.numpy.org

.. |Sphinx| replace:: Sphinx
.. _Sphinx: http://sphinx-doc.org

.. |TUG| replace:: TeX User Group
.. _TUG: http://sphinx-doc.org

.. an extended version of pdfTeX using Lua as an embedded scripting language
.. |LuaTeX| replace:: LuaTeX
.. _LuaTeX: http://www.luatex.org

.. |Knuth| replace:: Donald E. Knuth
.. _Knuth: http://www-cs-faculty.stanford.edu/~uno

.. |MathJax| replace:: MathJax
.. _MathJax: http://www.mathjax.org

.. A DVI-to-PNG converter
.. |dvipng| replace:: dvipng
.. _dvipng: http://savannah.nongnu.org/projects/dvipng

.. |Matplotlib| replace:: Matplotlib
.. _Matplotlib: http://matplotlib.org

.. |PGF| replace:: PGF
.. _PGF: http://sourceforge.net/projects/pgf

.. |Asymptote| replace:: Asymptote
.. _Asymptote: http://asymptote.sourceforge.net

.. |Circuit_macros| replace:: Circuit_macros
.. _Circuit_macros: https://ece.uwaterloo.ca/~aplevich/Circuit_macros

.. |pyqt| replace:: pyqt
.. _pyqt: http://www.riverbankcomputing.co.uk/software/pyqt/intro

.. |pillow| replace:: pillow
.. _pillow: http://pillow.readthedocs.org/en/latest/index.html

.. |PyOpenGLng| replace:: PyOpenGLng
.. _PyOpenGLng: https://github.com/FabriceSalvaire/PyOpenGLng

.. |freetype-py| replace:: freetype-py
.. _freetype-py: https://github.com/rougier/freetype-py

.. End

=========
 PyDvi
=========

The official PyDvi Home Page is located at |PyDviUrl|

The latest documentation build from the git repository is available at readthedocs.org |PyDvi@readthedocs-badge|

Written by `Fabrice Salvaire <http://fabrice-salvaire.pagesperso-orange.fr>`_.

|Build Status|

-----

.. image:: https://raw.github.com/FabriceSalvaire/PyDvi/master/doc/sphinx/source/images/dvi-gl-viewer.scaled.png

.. -*- Mode: rst -*-


==============
 Introduction
==============

.. link to TUG
.. library versus module

PyDvi is a |Python|_ library to read and process DVI (DeVice Independent) files, the native output
of the famous TeX typesetting program implemented by |Knuth|_.

PyDvi is also able to read most of the file formats associated to the TeX world like packed font,
virtual font, TeX font metric, font map and font encoding. It can also read Adobe Font Metrics files.

Basically a DVI file describes the layout of a page by a list of opcodes that interact with a
register machine to update the position on the page, to load fonts and to paint glyphs and rules. In
short it contains the glyphs and their positions on the page. Since TeX was designed to layout the
series of books *The Art of Computer Programming* at the beginning of the eighties, it focuses on
texts and mathematical expressions. Thus DVI is much simpler than Postscript or its successor PDF
which are designed for graphics. However we can extend the capabilities of DVI using the *special*
opcode which can contain any text like Postscript snippets.

A DVI stream can come from a file or a TeX daemon in order to render TeX inputs on-the-fly.

The DVI parser of PyDvi builds a program from a DVI stream that could be later processed by the
provided DVI machine which is designed to be subclassed by the user.

The source code includes an experimental DVI viewer as exemple which uses the OpenGL API for the
rendering and thus feature an hardware accelerated rendering. PyDvi and the viewer can be used as a
platform to experiment complex text rendering on GPU.

The source code includes also a clone of the |dvipng| tool to render DVI to PNG image. This tool is
mainly intended to check the compliance of PyDvi by image comparison.

.. The aim of PyDvi is multiple

PyDvi can be used for several purpose, we will review them in the followings:

TeX is a major and historical typesetting program. PyDvi can serve to read and process its output
using Python. The user can be a curious pearson who want to lean TeX or somebody interested by TeX
postprocessing.

TeX is one of the oldest computer program still in activity. The reason is quite simple, these
algorithms do the right job, its ecosystem is rich and its code is not so simple. Thus nobody
succeeds to reimplement it up to now, excepted its mathematical layout algorithms by the |Mathjax|_
Javascript library which is intended to bring Mathematical layout to web browser. Before the
delivery of Mathjax, the only solution to render properly mathematical content was to generate an
image using a program like |Dvipng|_. It is what does the engine of Wikipedia behind the scene.
Usually these programs like |Asymptote|_ or |Circuit_macros|_ generate the graphics as a PDF
document and then include this document in a LaTeX document which contains the labels placed at
absolute positions in the page. With PyDvi we can try another approach which consists to send TeX
content to a daemon and get back the glyphs and their positions. |Matplotlib|_ uses this approach to
render LaTeX labels.

.. -*- Mode: rst -*-

.. End

.. End

.. -*- Mode: rst -*-

.. _installation-page:


==============
 Installation
==============

The installation of PyDvi by itself is quite simple. However it will be easier to get the
dependencies on a Linux desktop.

Dependencies
------------

PyDvi requires the following dependencies:

 * |Python|_
 * |Numpy|_
 * |freetype-py|_ for Type1 font rendering

The OpenGL DVI viewer requires these additional dependencies:

 * |PyQt|_
 * |PyOpenGLng|_

The DVI to PNG tool requires these additional dependencies:

 * |pillow|_

Also it is recommanded to have these Python modules:

 * pip
 * virtualenv
 
For development, you will need in addition:

 * |Sphinx|_

Installation from PyPi Repository
---------------------------------

PyDvi is made available on the |Pypi|_ repository at |PyDvi@pypi|

Run this command to install the last release:

.. code-block:: sh

  pip install PyDvi

Installation from Source
------------------------

The PyDvi source code is hosted at |PyDvi@github|

To clone the Git repository, run this command in a terminal:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/PyDvi.git

Then to build and install PyDvi run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

.. End

.. End
