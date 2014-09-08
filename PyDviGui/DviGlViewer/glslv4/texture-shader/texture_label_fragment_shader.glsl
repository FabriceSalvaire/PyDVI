/* *********************************************************************************************** */

// #shader_type fragment

#version 330
// #version 420

/* *********************************************************************************************** */

// layout(binding=0)
uniform usampler2D texture0;
// %layout(binding=1)
uniform sampler1D random_label_texture;

/* *********************************************************************************************** */

in VertexAttributes
{
  vec2 uv;
} vertex;

/* *********************************************************************************************** */

out vec4 fragment_colour;

/* *********************************************************************************************** */

void main()
{
  ivec4 label_texel = ivec4(texture(texture0, vertex.uv));

  // Ok for 3 waves !
  if (label_texel == ivec4(0, 0, 0, 1))
    discard;

  int number_of_labels = 0;
  int label = 0;
  if (label_texel.r != 0)
    {
      number_of_labels += 1;
      label = label_texel.r;
    }
  if (label_texel.g != 0)
    {
      number_of_labels += 1;
      label = label_texel.g;
    }
  if (label_texel.b != 0)
    {
      number_of_labels += 1;
      label = label_texel.b;
    }
  /*
  if (label_texel.a != 0)
    {
      number_of_labels += 1;
      label = label_texel.a;
    }
  */
  if (number_of_labels == 0)
    fragment_colour.rgb = vec3(.0, .0, .0);
  else if (number_of_labels > 1)
    fragment_colour.rgb = vec3(1., 1., 1.);
  else
    {
      int random_label_texture_size = textureSize(random_label_texture, 0);
      int red_offset = 0;
      int green_offset = random_label_texture_size / 3;
      int blue_offset = (2 * random_label_texture_size) / 3;

      int texture_index;
      vec4 colour_texel;

      texture_index = (label + red_offset) % random_label_texture_size;
      colour_texel = texelFetch(random_label_texture, texture_index, 0);
      fragment_colour.r = colour_texel.r;

      texture_index = (label + green_offset) % random_label_texture_size;
      colour_texel = texelFetch(random_label_texture, texture_index, 0);
      fragment_colour.g = colour_texel.r;

      texture_index = (label + blue_offset) % random_label_texture_size;
      colour_texel = texelFetch(random_label_texture, texture_index, 0);
      fragment_colour.b = colour_texel.r;

      // fragment_colour = vec4(label_texel % 10) / 10.;
    }
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
