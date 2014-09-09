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

class TextVertexArray(GlVertexArrayObject):

    """ This class wraps a Text Vertex Array. """

    _logger = _module_logger.getChild('TextVertexArray')

    _uv_vbo = None

    ##############################################
    
    def __init__(self, image_texture):

        super(TextVertexArray, self).__init__()

        self._image_texture = image_texture # Fixme: could contains several font and size
        self._font_atlas_shape = image_texture.shape

        self._number_of_vertexes = 0
        self._vertexes, self._texture_coordinates, self._colours = self._create_arrays(0)

    ##############################################
    
    def _create_arrays(self, number_of_vertexes):

        vertexes = np.zeros((number_of_vertexes, 4), dtype=np.float32)
        texture_coordinates = np.zeros((number_of_vertexes, 4), dtype=np.float32)
        colours = np.zeros((number_of_vertexes, 4), dtype=np.float32)

        return vertexes, texture_coordinates, colours

    ##############################################
    
    def add(self, glyphs, colour):

        number_of_glyphs = len(glyphs)
        number_of_vertexes = number_of_glyphs
        vertexes, texture_coordinates, colours = self._create_arrays(number_of_vertexes)

        for i, glyph in enumerate(glyphs):
            char_bounding_box, glyph_texture_coordinates = glyph
            texture_coordinates[i] = glyph_texture_coordinates
            vertexes[i] = char_bounding_box
            colours[i] = colour

        # Concatenate the vertexes
        self._number_of_vertexes += number_of_vertexes
        self._vertexes = np.concatenate((self._vertexes, vertexes))
        self._texture_coordinates = np.concatenate((self._texture_coordinates, texture_coordinates))
        self._colours = np.concatenate((self._colours, colours))

    ##############################################
    
    def __del__(self):

        self._logger.debug('')
        super(TextVertexArray, self).__del__()

    ##############################################
    
    def upload(self):

        # Create VBO
        # self._logger.debug(str(self._vertexes))
        self._vertexes_vbo = GlArrayBuffer(self._vertexes)
        self._texture_coordinates_vbo = GlArrayBuffer(self._texture_coordinates)
        self._colours_vbo = GlArrayBuffer(self._colours)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface):

        self.bind()

        shader_program_interface.position.bind_to_buffer(self._vertexes_vbo) # self._vertex_vbo
        shader_program_interface.position_uv.bind_to_buffer(self._texture_coordinates_vbo) # self._uv_vbo
        shader_program_interface.colour.bind_to_buffer(self._colours_vbo)

        # Texture unit as default
        # shader_program.uniforms.texture0 = 0

        self.unbind()

    ##############################################
    
    def draw(self, shader_program):

        # Blending: O = Sf*S + Df*D
        #  where S is the colour from the fragment shader and D the colour from the framebuffer
        #   alpha: fully transparent = 0 and fully opaque = 1
        #   Sa = average luminosity * colour aplha
        #
        # Set (Sf, Df) for transparency: O = Sa*S + (1-Sa)*D 

        GL.glEnable(GL.GL_BLEND)
        # GL.glBlendEquation(GL.GL_FUNC_ADD)
        # GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_SRC_ALPHA) # Fixme: check cf. fragment shader

        shader_program.bind()
        self._image_texture.bind()
        self.bind()

        shader_program.uniforms.font_atlas = 0
        # shader_program.uniforms.gamma = 1.

        GL.glDrawArrays(GL.GL_POINTS, 0, self._number_of_vertexes)

        self.unbind()
        self._image_texture.unbind()
        shader_program.unbind()

        GL.glDisable(GL.GL_BLEND)

####################################################################################################
# 
# End
# 
####################################################################################################
