####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

import logging

from PyQt4 import QtCore

import numpy as np

####################################################################################################

#!# from PyOpenGLng.HighLevelApi.GlOrtho2D import ZoomManagerAbc

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlUniformBuffer
from PyOpenGLng.HighLevelApi.Geometry import Point, Offset, Segment, Rectangle
from PyOpenGLng.HighLevelApi.GlWidgetBase import GlWidgetBase
from PyOpenGLng.HighLevelApi.ImageTexture import ImageTexture
from PyOpenGLng.HighLevelApi.PrimitiveVertexArray import GlSegmentVertexArray, GlRectangleVertexArray
from PyOpenGLng.Tools.Interval import IntervalInt2D

from .TextVertexArray import TextVertexArray

####################################################################################################

class GlWidget(GlWidgetBase):

    logger = logging.getLogger(__name__)
 
    ##############################################
    
    def __init__(self, parent):

        self.logger.debug('Initialise GlWidget')

        super(GlWidget, self).__init__(parent)

    ##############################################

    def wheelEvent(self, event):

        self.logger.debug('Wheel Event')

        return self.wheel_zoom(event)

    ##############################################

    def init_glortho2d(self):

        # Set max_area so as to correspond to max_binning zoom centered at the origin
        page_width = 210 # mm
        page_height = 297
        # max_area = IntervalInt2D([0, page_width], [0, page_height])
        # max_area.enlarge(100)
        area_size = 10**3
        max_area = IntervalInt2D([-area_size, area_size], [-area_size, area_size])

        super(GlWidget, self).init_glortho2d(max_area, zoom_manager=None)

    ##############################################

    def initializeGL(self):

        self.logger.debug('Initialise GL')

        super(GlWidget, self).initializeGL()

        GL.glEnable(GL.GL_POINT_SMOOTH) #compat# 
        GL.glEnable(GL.GL_LINE_SMOOTH) #compat# 
        
        self.qglClearColor(QtCore.Qt.black)
        #!# self.qglClearColor(QtCore.Qt.white)
        # GL.glPointSize(5.)
        # GL.glLineWidth(3.)

        self._init_shader()
        self.create_vertex_array_objects()

    ##############################################

    def _init_shader(self):

        self.logger.debug('Initialise Shader')

        import ShaderProgramesV4 as ShaderProgrames
        self.shader_manager = ShaderProgrames.shader_manager
        self.position_shader_interface = ShaderProgrames.position_shader_program_interface

        # Fixme: share interface
        self._viewport_uniform_buffer = GlUniformBuffer()
        viewport_uniform_block = self.position_shader_interface.uniform_blocks.viewport
        self._viewport_uniform_buffer.bind_buffer_base(viewport_uniform_block.binding_point)

    ##############################################

    def update_model_view_projection_matrix(self):

        self.logger.debug('Update Model View Projection Matrix'
                         '\n' + str(self.glortho2d))

        viewport_uniform_buffer_data = self.glortho2d.viewport_uniform_buffer_data(self.size())
        self.logger.debug('Viewport Uniform Buffer Data '
                          '\n' + str(viewport_uniform_buffer_data))
        self._viewport_uniform_buffer.set(viewport_uniform_buffer_data)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_page_layout()
        self.create_text()

    ##############################################

    def create_page_layout(self): # , page_bounding_box

        page_width = 210 # mm
        page_height = 297

        # (page_x_min, page_y_min,
        #  text_width, text_height) = map(sp2mm,
        #                                 (page_bounding_box.x.inf,
        #                                  page_bounding_box.y.inf,
        #                                  page_bounding_box.x.length(),
        #                                  page_bounding_box.y.length(),
        #                                  ))

        rectangles = (Rectangle(Point(0, 0), Offset(page_width, page_height)),)
        self.rectangle_vertex_array = GlRectangleVertexArray(rectangles)
        self.rectangle_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

        segments = []

        grid_spacing = 5
        x = grid_spacing
        while x < page_width:
            p1 = Point(x, 0)
            p2 = Point(x, page_height)
            segments.append(Segment(p1, p2))
            x += grid_spacing

        y = grid_spacing
        while y < page_height:
            p1 = Point(0, y)
            p2 = Point(page_width, y)
            segments.append(Segment(p1, p2))
            y += grid_spacing
        
        self.grid_vertex_array = GlSegmentVertexArray(segments)
        self.grid_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

    ##############################################

    def update_dvi(self, dvi_machine):

        self._dvi_machine = dvi_machine

    ##############################################

    def create_text(self, ):

        dvi_machine = self._dvi_machine

        self._text_vertex_arrays = []
        rectangles = []
        for texture_font in dvi_machine._texture_fonts.itervalues():
            texture_font.atlas.save(texture_font.name + '.png')
            font_atlas_texture = ImageTexture(texture_font.atlas.data)
            text_vertex_array = TextVertexArray(font_atlas_texture)
            glyphs = dvi_machine._glyphs[texture_font.name]
            text_vertex_array.add(glyphs=glyphs, colour=(1.0, 1.0, 1.0, 1.0))
            text_vertex_array.upload()
            text_vertex_array.bind_to_shader(self.shader_manager.text_shader_program.interface.attributes)
            self._text_vertex_arrays.append(text_vertex_array)

            for i, glyph in enumerate(glyphs):
                char_bounding_box, glyph_texture_coordinates = glyph
                x, y, width, height = char_bounding_box
                rectangles.append(Rectangle(Point(x, y), Offset(width, height)))

        self._char_bounding_box_vertex_array = GlRectangleVertexArray(rectangles)
        self._char_bounding_box_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

    ##############################################

    def paint(self):

        self._logger.info('')
        self.paint_page_layout()
        self.paint_text()

    ##############################################

    def paint_page_layout(self):

        self._logger.info('')
        shader_program = self.shader_manager.rectangle_shader_program
        shader_program.bind()
        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (1., 0., 1.)
        self.rectangle_vertex_array.draw()

        shader_program = self.shader_manager.fixed_shader_program
        shader_program.bind()
        GL.glLineWidth(1.)
        shader_program.uniforms.colour = (1., 1., 1.)
        self.grid_vertex_array.draw()
        shader_program.unbind()

    ##############################################

    def paint_text(self):

        shader_program = self.shader_manager.text_shader_program
        # shader_program.bind()
        # shader_program.uniforms. ...
        for text_vertex_array in self._text_vertex_arrays:
            self._logger.info('paint text')
            text_vertex_array.draw(shader_program)
        # shader_program.unbind()

        self._logger.info('Paint char bounding boxes')
        shader_program = self.shader_manager.rectangle_shader_program
        shader_program.bind()
        GL.glLineWidth(1.)
        shader_program.uniforms.colour = (1., 0., 0.)
        self._char_bounding_box_vertex_array.draw()

####################################################################################################
#
# End
#
####################################################################################################
