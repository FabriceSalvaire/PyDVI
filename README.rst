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

.. End

=========
 PyDvi
=========

The official PyDvi Home Page is located at |PyDviUrl|

The latest documentation build from the git repository is available at readthedocs.org |PyDvi@readthedocs-badge|

Written by `Fabrice Salvaire <http://fabrice-salvaire.pagesperso-orange.fr>`_.

|Build Status|

-----

.. -*- Mode: rst -*-


==============
 Introduction
==============

PyDvi is a |Python|_ library that provides tools to read TeX DVI file, Packed Font and TeX Font
Metric, Font Map and Font Encoding. The library provides a DVI Machine base class hat can be plugged
to a TeX Daemon instance in order to render on-the-fly TeX inputs.

.. -*- Mode: rst -*-

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
 * PyQt
 * freetype

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
