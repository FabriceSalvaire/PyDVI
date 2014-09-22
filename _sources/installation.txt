.. -*- Mode: rst -*-

.. _installation-page:

.. include:: project-links.txt
.. include:: abbreviation.txt

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
