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
#  - 10/01/2010 fabrice
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['kpsewhich']

#####################################################################################################

import subprocess

#####################################################################################################

def kpsewhich(filename, file_format=None, options=None):

    """Wrapper around kpsewhich program
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
