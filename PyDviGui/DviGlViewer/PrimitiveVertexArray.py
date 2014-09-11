####################################################################################################
# 
# PyDvi - A Python Library to Process DVI Stream
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
####################################################################################################

####################################################################################################

import logging
import numpy as np

####################################################################################################

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlArrayBuffer
from PyOpenGLng.HighLevelApi.VertexArrayObject import GlVertexArrayObject

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: complete PyOpenGLng HighLevelApi

class GlPointVertexArray(GlVertexArrayObject):

    """ Base class to draw primitives as points. """

    ##############################################
    
    def __init__(self, items=None):

        super(GlPointVertexArray, self).__init__()

        self._number_of_items = 0
        self._vertex_array_buffer = GlArrayBuffer()

        if items is not None:
            self.set(items)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface_attribute):

        """ Bind the vertex array to the shader program interface attribute.
        """

        self.bind()
        shader_program_interface_attribute.bind_to_buffer(self._vertex_array_buffer)
        self.unbind()

    ##############################################
    
    def set(self, items):

        """ Set the vertex array from a numpy array. """

        self._number_of_items = items.shape[0]

        # make copy
        vertex = np.array(items, dtype='f') # dtype=np.float

        self._vertex_array_buffer.set(vertex)

    ##############################################
    
    def draw(self):

        """ Draw the vertex array as points. """

        self.bind()
        GL.glDrawArrays(GL.GL_POINTS, 0, self._number_of_items)
        self.unbind()

####################################################################################################

class RuleVertexArray(GlVertexArrayObject):

    _logger = _module_logger.getChild('RuleVertexArray')

    ##############################################
    
    def __init__(self, items=None):

        super(RuleVertexArray, self).__init__()

        self._number_of_items = 0
        # Fixme: _buffer or _vbo
        self._positions_buffer = GlArrayBuffer() # could pass data here
        self._dimensions_buffer = GlArrayBuffer()
        self._colours_buffer = GlArrayBuffer()

        if items is not None:
            self.set(items)

    ##############################################
    
    def set(self, items):

        """ Set the vertex array from a numpy array. """

        self._number_of_items = items.shape[0]

        # Fixme: we recreate the arrays
        positions = np.array(items[:,:2], dtype='f') # dtype=np.float
        dimensions = np.array(items[:,2:4], dtype='f') # dtype=np.float
        colours = np.array(items[:,4:], dtype='f') # dtype=np.float

        self._positions_buffer.set(positions)
        self._dimensions_buffer.set(dimensions)
        self._colours_buffer.set(colours)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface):

        self.bind()
        shader_program_interface.position.bind_to_buffer(self._positions_buffer)
        shader_program_interface.dimension.bind_to_buffer(self._dimensions_buffer)
        shader_program_interface.colour.bind_to_buffer(self._colours_buffer)
        self.unbind()

    ##############################################
    
    def draw(self):

        self.bind()
        GL.glDrawArrays(GL.GL_POINTS, 0, self._number_of_items)
        self.unbind()

####################################################################################################
#
# End
#
####################################################################################################
