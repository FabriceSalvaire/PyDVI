/* *********************************************************************************************** */

// #shader_type vertex

#version 330

/* *********************************************************************************************** */

#include(../include/model_view_projection_matrix.glsl)
#include(../include/position_shader_program_interface.glsl)

/* *********************************************************************************************** */

in vec3 colour;

/* *********************************************************************************************** */

out VertexAttributes
{
  vec4 colour;
} vertex;

/* *********************************************************************************************** */

void main()
{
  gl_Position = model_view_projection_matrix * vec4(position, 0, 1);
  vertex.colour = colour;
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
