/* *********************************************************************************************** */

// #shader_type geometry

#version 330
#extension GL_EXT_geometry_shader4 : enable

/* *********************************************************************************************** */

#include(../include/model_view_projection_matrix.glsl)

/* *********************************************************************************************** */

layout(lines) in;
layout(line_strip, max_vertices=5) out;

/* *********************************************************************************************** */

in VertexAttributesIn
{
  vec2 position;
  vec4 colour;
} vertexIn[];

/* *********************************************************************************************** */

out VertexAttributes
{
  vec4 colour;
} vertex;

/* *********************************************************************************************** */

void emit_vertex()
{
  gl_Position = model_view_projection_matrix * vec4(vertexIn[0].position, 0, 1);
  EmitVertex();
}

void emit_vertex_add(vec2 offset)
{
  vec2 position = vertexIn[0].position + offset;
  gl_Position = model_view_projection_matrix * vec4(position, 0, 1);
  EmitVertex();
}

/* *********************************************************************************************** */

void main()
{
  vertex.colour = vertexIn[0].colour;

  vec2 pos1 = vertexIn[1].position;
  emit_vertex();
  emit_vertex_add(vec2(pos1.x, 0));
  emit_vertex_add(pos1);
  emit_vertex_add(vec2(0, pos1.y));
  emit_vertex();
  EndPrimitive();
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
