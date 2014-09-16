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

from PyQt4 import QtCore, QtGui

####################################################################################################

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlUniformBuffer
from PyOpenGLng.HighLevelApi.Geometry import Point, Offset, Segment, Rectangle
from PyOpenGLng.HighLevelApi.GlWidgetBase import GlWidgetBase
from PyOpenGLng.HighLevelApi.ImageTexture import ImageTexture
from PyOpenGLng.HighLevelApi.Ortho2D import XAXIS, YAXIS
from PyOpenGLng.HighLevelApi.PrimitiveVertexArray import GlSegmentVertexArray, GlRectangleVertexArray
from PyOpenGLng.Tools.Interval import IntervalInt2D

####################################################################################################

from .TextVertexArray import TextVertexArray
from .PrimitiveVertexArray import RuleVertexArray
# from .RuleVertexArray import RuleVertexArray

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlWidget(GlWidgetBase):

    _logger = _module_logger.getChild('GlWidget')
 
    ##############################################
    
    def __init__(self, parent, main_window):

        self._logger.debug('Initialise GlWidget')
        super(GlWidget, self).__init__(parent)

        self._application = QtGui.QApplication.instance()
        self._main_window = main_window # self._application.main_window # not yet initialised

        self.x_step = 5 # mm
        self.y_step = 5 # mm
        self.zoom_step = 1.10 # must be float

    ##############################################

    def init_glortho2d(self):

        # Set max_area so as to correspond to max_binning zoom centered at the origin
        a0_width = 840 # mm 
        a0_height = 1189
        max_area = IntervalInt2D([0, a0_height], [0, a0_height])
        max_area.enlarge(a0_height)

        super(GlWidget, self).init_glortho2d(max_area, zoom_manager=None)

    ##############################################

    def initializeGL(self):

        self._logger.debug('Initialise GL')
        super(GlWidget, self).initializeGL()

        GL.glEnable(GL.GL_POINT_SMOOTH) #compat# 
        GL.glEnable(GL.GL_LINE_SMOOTH) #compat# 

        self._init_shader()
        self._paint_page = False

    ##############################################

    def _init_shader(self):

        self._logger.debug('Initialise Shader')

        import ShaderProgramesV4 as ShaderProgrames
        self.shader_manager = ShaderProgrames.shader_manager
        self.position_shader_interface = ShaderProgrames.position_shader_program_interface
        self.rule_shader_interface = ShaderProgrames.rule_shader_program_interface
        self.text_shader_interface = ShaderProgrames.text_shader_program_interface

        # Fixme: share interface
        self._viewport_uniform_buffer = GlUniformBuffer()
        viewport_uniform_block = self.position_shader_interface.uniform_blocks.viewport
        self._viewport_uniform_buffer.bind_buffer_base(viewport_uniform_block.binding_point)

    ##############################################

    def update_model_view_projection_matrix(self):

        self._logger.debug('Update Model View Projection Matrix'
                           '\n' + str(self.glortho2d))

        viewport_uniform_buffer_data = self.glortho2d.viewport_uniform_buffer_data(self.size())
        self._logger.debug('Viewport Uniform Buffer Data '
                           '\n' + str(viewport_uniform_buffer_data))
        self._viewport_uniform_buffer.set(viewport_uniform_buffer_data)

    ##############################################

    def _create_page_layout(self, width, height):

        self._page_width = width
        self._page_height = height

        # (page_x_min, page_y_min,
        #  text_width, text_height) = map(sp2mm,
        #                                 (page_bounding_box.x.inf,
        #                                  page_bounding_box.y.inf,
        #                                  page_bounding_box.x.length(),
        #                                  page_bounding_box.y.length(),
        #                                  ))

        rectangles = (Rectangle(Point(0, 0), Offset(width, height)),)
        self.rectangle_vertex_array = GlRectangleVertexArray(rectangles)
        self.rectangle_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

        segments = []

        grid_spacing = 5
        x = grid_spacing
        while x < width:
            p1 = Point(x, 0)
            p2 = Point(x, height)
            segments.append(Segment(p1, p2))
            x += grid_spacing

        y = grid_spacing
        while y < height:
            p1 = Point(0, y)
            p2 = Point(width, y)
            segments.append(Segment(p1, p2))
            y += grid_spacing
        
        self.grid_vertex_array = GlSegmentVertexArray(segments)
        self.grid_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

    ##############################################

    def update_dvi(self, dvi_machine):

        self._logger.info('Update DVI')

        self._text_vertex_arrays = []
        for font_id, glyphs in dvi_machine.glyphs.iteritems():
            texture_font = dvi_machine.texture_fonts[font_id]
            # texture_font.atlas.save(texture_font.name + '.png')
            font_atlas_texture = ImageTexture(texture_font.atlas.data)
            positions, bounding_boxes, texture_coordinates, colours = glyphs
            items = (positions, texture_coordinates, colours)
            text_vertex_array = TextVertexArray(font_atlas_texture, items)
            text_vertex_array.bind_to_shader(self.text_shader_interface.attributes)
            self._text_vertex_arrays.append(text_vertex_array)

        #     for glyph in glyphs:
        #         glyph_bounding_box, char_bounding_box, glyph_texture_coordinates = glyph
        #         x, y, width, height = char_bounding_box
        #         rectangles.append(Rectangle(Point(x, y), Offset(width, height)))

        # self._char_bounding_box_vertex_array = GlRectangleVertexArray(rectangles)
        # self._char_bounding_box_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

        self._rule_vertex_array = RuleVertexArray((dvi_machine.rule_positions,
                                                   dvi_machine.rule_dimensions,
                                                   dvi_machine.rule_colours))
        self._rule_vertex_array.bind_to_shader(self.rule_shader_interface.attributes)

        width = dvi_machine.current_opcode_program.width
        height = dvi_machine.current_opcode_program.height
        if not width or not height: 
            first_page = dvi_machine.dvi_program[0]
            width, height = first_page.width, first_page.height
        if not width or not height:
            self._logger.warning('Page size is null')
            width, height = 210, 297 # use A4
        self._create_page_layout(width, height)

        self._logger.info('update DVI done')

        self._paint_page = True

        self.fit_document()

    ##############################################

    def update(self):

        super(GlWidget, self).update()
        if self._paint_page:
            self._update_zoom_status()

    ##############################################

    def resizeGL(self, width, height):

        super(GlWidget, self).resizeGL(width, height)

        dpi = self._application.platform.screens[0].dpi[0]
        self._width_widget_mm = width/float(dpi)*25.4

    ##############################################

    def _update_zoom_status(self):

        # xdpyinfo:
        #   dimensions:    1600x900 pixels (423x238 millimeters) # Wrong !!!
        #   resolution:    96x96 dots per inch
        # monitor-edid:
        #   Screen size: 30.9 cm x 17.4 cm (13.96 inches, aspect ratio 16/9 = 1.78)
        # 1600/(309./25.4) -> 131 dpi

        # gl_zoom = self.glortho2d.zoom_manager.zoom_factor
        area = self.glortho2d.viewport_area.area
        zoom = self._width_widget_mm / area.x.length() 
        self._main_window.status_bar.update_zoom_status(zoom)

    ##############################################

    def paint(self):

        self._logger.info('')
        # Clear the buffer using white colour (white paper)
        GL.glClearColor(1, 1, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if self._paint_page:
            self._paint_page_layout()
            self._paint_text()

    ##############################################

    def _paint_page_layout(self):

        self._logger.debug('')
        shader_program = self.shader_manager.rectangle_shader_program
        shader_program.bind()
        # GL.glLineWidth(1.)
        shader_program.uniforms.colour = (.0, 0., .0)
        self.rectangle_vertex_array.draw()

        if False:
            shader_program = self.shader_manager.fixed_shader_program
            shader_program.bind()
            # GL.glLineWidth(.1) # Fixme: do in shader ...
            shader_program.uniforms.colour = (.0, .0, .1)
            self.grid_vertex_array.draw()
            shader_program.unbind()

    ##############################################

    def _paint_text(self):

        shader_program = self.shader_manager.text_shader_program
        # shader_program.bind()
        # shader_program.uniforms. ...
        for text_vertex_array in self._text_vertex_arrays:
            self._logger.debug('paint text')
            text_vertex_array.draw(shader_program)
        # shader_program.unbind()

        if False:
            self._logger.debug('Paint char bounding boxes')
            shader_program = self.shader_manager.rectangle_shader_program
            shader_program.bind()
            # GL.glLineWidth(1.)
            shader_program.uniforms.colour = (1., 0., 0.)
            self._char_bounding_box_vertex_array.draw()

        self._logger.debug('Paint rules')
        # Fixme: anti-alias
        shader_program = self.shader_manager.rule_shader_program
        shader_program.bind()
        self._rule_vertex_array.draw()

    ##############################################

    def wheelEvent(self, event):

        self._logger.debug('Wheel Event')
        return self.wheel_zoom(event)

    ##############################################

    def mousePressEvent(self, event):

        if event.buttons() & QtCore.Qt.LeftButton:
            self._show_coordinate(event)

    ##############################################

    def mouseMoveEvent(self, event):

        self._show_coordinate(event)
                
    ##############################################

    def _show_coordinate(self, event):

        coordinate = self.window_to_gl_coordinate(event)
        x, y = coordinate
        y = self._page_height - y
        self._main_window.status_bar.update_coordinate_status(x, y)

    ##############################################

    def fit_width(self):

        if self._paint_page:
            self.glortho2d.fit_axis(self._page_width, XAXIS)
            self.update()

    ##############################################

    def fit_document(self):

        if self._paint_page:
            interval = IntervalInt2D((0, self._page_width), (0, self._page_height))
            interval.enlarge(10) # mm
            self.zoom_interval(interval)

    ##############################################

    def translate_x(self, dx):

        area = self.glortho2d.viewport_area.area
        # Fixme: cf. check_axis_interval
        if ((dx > 0 and area.x.sup + dx <= self._page_width)
            or (dx < 0 and area.x.inf + dx >= 0)):
            self.glortho2d.translate(dx, XAXIS)
            self.update()

    ##############################################

    def translate_y(self, dy):

        area = self.glortho2d.viewport_area.area
        # Fixme: cf. check_axis_interval
        if ((dy > 0 and area.y.sup + dy <= self._page_height)
            or (dy < 0 and area.y.inf + dy >= 0)):
            self.glortho2d.translate(dy, YAXIS)
            self.update()

    ##############################################

    def zoom_in_out(self, direction):

        zoom_factor = self.glortho2d.zoom_manager.zoom_factor
        if direction > 0:
            zoom_factor *= self.zoom_step
        else:
            zoom_factor /= self.zoom_step
        self.glortho2d.zoom_at_center(zoom_factor)
        self.update()

####################################################################################################
#
# End
#
####################################################################################################
