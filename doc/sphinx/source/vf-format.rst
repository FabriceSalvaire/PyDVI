==========================
 Virtual Font File Format
==========================

The Virtual Font file format is described in the :file:`vftovp.web` file from Web2C.  Part of this
documentation comes from this file.

The idea behind VF files is that a general interface mechanism is needed to switch between the
myriad font layouts provided by different suppliers of typesetting equipment. Without such
mechanism, people must go to great lengths writing inscrutable macros whenever they want to use
typesetting conventions based on one font layout in connection with actual fonts that have another
layout. This puts an extra burden on the typesetting system, interfering with the other things it
needs to do (like kerning, hyphenation, and ligature formation).

These difficulties go away when we have a “virtual font,” i.e., a font that exists in a logical
sense but not a physical sense. A typesetting system like TEX can do its job without knowing where
the actual characters come from; a device driver can then do its job by letting a VF file tell what
actual characters correspond the characters TEX imagined were present. The actual characters can be
shifted and/or magnified and/or combined with other characters from many different fonts. A virtual
font can even make use of characters from virtual fonts, including itself.

Virtual fonts also allow convenient character substitutions for proofreading purposes, when fonts
designed for one output device are unavailable on another.

A VF file is organised as a stream of 8-bit bytes, using conventions borrowed from DVI and PK files.
Thus, a device driver that knows about DVI and PK format will already contain most of the mechanisms
necessary to process VF files. We shall assume that DVI format is understood; the conventions in the
DVI documentation (see, for example, TEX: The Program, part 31) are adopted here to define VF
format.

A preamble appears at the beginning, followed by a sequence of character definitions, followed by a
postamble. More precisely, the first byte of every VF file must be the first byte of the following
“preamble command”: ``pre 247 i[1] k[1] x[k] cs [4] ds [4]``. Here ``i`` is the identification byte
of VF, currently 202. The string ``x`` is merely a comment, usually indicating the source of the VF
file. Parameters ``cs`` and ``ds`` are respectively the check sum and the design size of the virtual
font; they should match the first two words in the header of the TFM file, as described below.

After the ``pre`` command, the preamble continues with font definitions; every font needed to
specify “actual” characters in later set char commands is defined here. The font definitions are
exactly the same in VF files as they are in DVI files, except that the scaled size ``s`` is relative
and the design size ``d`` is absolute:

* ``fnt def1 243 k[1] c[4] s[4] d[4] a[1] l[1] n[a + l]``. Define font ``k``, where 0 ≤ k < 256.
* ``fnt def2 244 k[2] c[4] s[4] d[4] a[1] l[1] n[a + l]``. Define font ``k``, where 0 ≤ k < 65536.
* ``fnt def3 245 k[3] c[4] s[4] d[4] a[1] l[1] n[a + l]``. Define font ``k``, where 0 ≤ k < 2**24.
* ``fnt def4 246 k[4] c[4] s[4] d[4] a[1] l[1] n[a + l]``. Define font ``k``, where −2**31 ≤ k < 2**31.

These font numbers ``k`` are “local”; they have no relation to font numbers defined in the DVI file
that uses this virtual font. The dimension ``s``, which represents the scaled size of the local font
being defined, is a fix word relative to the design size of the virtual font. Thus if the local font
is to be used at the same size as the design size of the virtual font itself, ``s`` will be the
integer value 2**20. The value of ``s`` must be positive and less than 2**24 (thus less than 16 when
considered as a fix word ). The dimension d is a fix word in units of printer’s points; hence it is
identical to the design size found in the corresponding TFM file.

The preamble is followed by zero or more character packets, where each character packet begins with
byte that is < 243. Character packets have two formats, one long and one short:

* ``long char 242 pl [4] cc [4] tfm [4] dvi [pl ]``. This long form specifies a virtual character in the general case.
* ``short char0 ... short char241 pl [1] cc [1] tfm [3] dvi [pl ]``. This short form specifies a
  virtual character in the common case when 0 ≤ pl < 242 and 0 ≤ cc < 256 and 0 ≤ tfm < 2**24.

Here ``pl`` denotes the packet length following the tfm value; ``cc`` is the character code; and
``tfm`` is the character width copied from the TFM file for this virtual font. There should be at
most one character packet having any given ``cc`` code.

The ``dvi`` bytes are a sequence of complete DVI commands, properly nested with respect to push and
pop.  All DVI operations are permitted except ``bop``, ``eop``, and commands with opcodes
≥ 243. Font selection commands (``fnt_num0`` through ``fnt4``) must refer to fonts defined in the
preamble.

Dimensions that appear in the DVI instructions are analogous to fix word quantities; i.e., they are
integer multiples of 2**−20 times the design size of the virtual font. For example, if the virtual
font has design size 10 pt, the DVI command to move down 5 pt would be a down instruction with
parameter 2**19. The virtual font itself might be used at a different size, say 12 pt; then that
down instruction would move down 6 pt instead. Each dimension must be less than 2**24 in absolute
value.

Device drivers processing VF files treat the sequences of dvi bytes as subroutines or macros,
implicitly enclosing them with push and pop. Each subroutine begins with ``w = x = y = z = 0``, and
with current font ``f`` the number of the first-defined in the preamble (undefined if there’s no
such font). After the dvi commands have been performed, the ``h`` and ``v`` position registers of
DVI format and the current font ``f`` are restored to their former values; then, if the subroutine
has been invoked by a set char or set command, ``h`` is increased by the TFM width (properly
scaled)—just as if a simple character had been typeset.

* long char = 242 { VF command for general character packet }
* set char 0 = 0 { DVI command to typeset character 0 and move right }
* set1 = 128 { typeset a character and move right }
* set rule = 132 { typeset a rule and move right }
* put1 = 133 { typeset a character }
* put rule = 137 { typeset a rule }
* nop = 138 { no operation }
* push = 141 { save the current positions }
* pop = 142 { restore previous positions }
* right1 = 143 { move right }
* w0 = 147 { move right by w }
* w1 = 148 { move right and set w }
* x0 = 152 { move right by x }
* x1 = 153 { move right and set x }
* down1 = 157 { move down }
* y0 = 161 { move down by y }
* y1 = 162 { move down and set y }
* z0 = 166 { move down by z }
* z1 = 167 { move down and set z }
* fnt num 0 = 171 { set current font to 0 }
* fnt1 = 235 { set current font }
* xxx1 = 239 { extension to DVI primitives }
* xxx4 = 242 { potentially long extension to DVI primitives }
* fnt def1 = 243 { define the meaning of a font number }
* pre = 247 { preamble }
* post = 248 { postamble beginning }
* improper DVI for VF ≡ 139, 140, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255

The character packets are followed by a trivial postamble, consisting of one or more bytes all equal
to post (248). The total number of bytes in the file should be a multiple of 4.

.. End
