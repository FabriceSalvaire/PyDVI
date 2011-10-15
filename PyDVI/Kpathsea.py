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
#  - 09/10/2011 Fabrice
#
#####################################################################################################

"""
This modules provides wrappers for the **Kpathsea** library.
"""

#####################################################################################################

__ALL__ = ['kpsewhich']

#####################################################################################################

import subprocess

#####################################################################################################

def kpsewhich(filename, file_format=None, options=None):

    """Wrapper around *kpsewhich* program

    *file_format*
      used to specify the file format, see *kpsewhich* help for the file format list

    *options*
      use it to give additional option to *kpsewhich*

    Examples::

       filename = kpsewhich('cmr10', file_format='tfm')
    """

    command = ['kpsewhich']
    if file_format is not None:
        command.append("--format='%s'" % (file_format))
    if options is not None:
        command.append(options)
    command.append(filename)

    shell_command = ' '.join(command)
    pipe = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE)
    stdout = pipe.communicate()[0]
    path = stdout.rstrip()

    return path if path else None

#####################################################################################################
#
# End
#
#####################################################################################################
