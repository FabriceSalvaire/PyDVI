/* *********************************************************************************************** */

// #shader_type geometry

#version 330
#extension GL_EXT_geometry_shader4 : enable

/* *********************************************************************************************** */

#include(../include/model_view_projection_matrix.glsl)

/* *********************************************************************************************** */

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

/* *********************************************************************************************** */

uniform vec2 font_atlas_shape;

/* *********************************************************************************************** */

in VertexAttributesIn
{
  vec4 position;
  vec4 uv;
  vec4 colour;
} vertexIn[];

/* *********************************************************************************************** */

out VertexAttributes
{
  vec2 uv;
  float horizontal_offset;
  vec4 colour;
} vertex;

/* *********************************************************************************************** */

void emit_vertex(vec2 position, vec2 uv)
{
  gl_Position =  model_view_projection_matrix * vec4(position, 0, 1);
  vertex.uv = uv;
  EmitVertex();
}

/* *********************************************************************************************** */

void main()
{
  vec2 position = vertexIn[0].position.xy;
  vec2 glyph_size = vertexIn[0].position.zw; // Fixme:
  vertex.horizontal_offset = fract(position.x);

  vec2 uv1 = vertexIn[0].uv.xy;
  vec2 uv2 = vertexIn[0].uv.zw;

  vertex.colour = vertexIn[0].colour;

  emit_vertex(position + vec2(0, glyph_size.y), uv1);
  emit_vertex(position + vec2(0, 0), vec2(uv1.s, uv2.t));
  emit_vertex(position + vec2(glyph_size.x, glyph_size), vec2(uv2.s, uv1.t));
  emit_vertex(position + vec2(glyph_size.x, 0), uv2);
  EndPrimitive();
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
