/* *********************************************************************************************** */

// #shader_type fragment

#version 330

/* *********************************************************************************************** */

uniform sampler2D font_atlas;
uniform vec2 font_atlas_shape;
uniform float gamma = 1.0;

/* *********************************************************************************************** */

in VertexAttributes
{
  vec2 uv;
  float horizontal_offset;
  vec4 colour;
} vertex;

/* *********************************************************************************************** */

out vec4 fragment_colour;

/* *********************************************************************************************** */

void main()
{
  // The glyphs are rendered in white (grayscale or LCD RGB anti-aliasing) in the font atlas.

  // lcd Filter
  vec4 current = texture2D(font_atlas, vertex.uv);
  vec4 previous = texture2D(font_atlas, vertex.uv + vec2(-1.,.0)*(1./font_atlas_shape));
  // vec4 next = texture2D(font_atlas, vertex.uv + vec2(+1.,.0)*(1./font_atlas_shape));

  float r = current.r;
  float g = current.g;
  float b = current.b;

  /*
  float r = 0;
  float g = 0;
  float b = 0;
  if (vertex.horizontal_offset <= 0.333)
    {
      float z = vertex.horizontal_offset / 0.333;
      r = mix(current.r, previous.b, z);
      g = mix(current.g, current.r, z);
      b = mix(current.b, current.g, z);
    } 
  else if (vertex.horizontal_offset <= 0.666)
    {
      float z = (vertex.horizontal_offset - 0.33) / 0.333;
      r = mix(previous.b, previous.g, z);
      g = mix(current.r, previous.b, z);
      b = mix(current.g, current.r, z);
    }
  else if (vertex.horizontal_offset < 1.0)
    {
      float z = (vertex.horizontal_offset - 0.66) / 0.334;
      r = mix(previous.g, previous.r, z);
      g = mix(previous.b, previous.g, z);
      b = mix(current.r, previous.b, z);
    }
  */

  // Gamma correction
  // Standard LCD Gamma: Out = IN**2.2
  vec3 rgb = pow(vec3(r,g,b), vec3(gamma));

  // note: black colour is null
  fragment_colour.rgb = rgb * vertex.colour.rgb;
  // alpha = 1 means fully opaque while alpha = 0 means fully transparent
  float average_luminosity = (rgb.r + rgb.g + rgb.b)/3.;
  fragment_colour.a = 1 - (average_luminosity * vertex.colour.a); // Fixme: check cf. blending
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
