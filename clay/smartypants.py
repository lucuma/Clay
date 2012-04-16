# -*- coding: utf-8 -*-
r"""
================
SmartyPants
================

Smart-quotes, smart-ellipses, and smart-dashes.

SmartyPants can perform the following transformations:

- Straight quotes ( " and ' ) into "curly" quote HTML entities
- Backticks-style quotes (\`\`like this'') into "curly" quote HTML entities
- Dashes (``--`` and ``---``) into en- and em-dash entities
- Three consecutive dots (``...`` or ``. . .``) into an ellipsis entity

This means you can write, edit, and save your posts using plain old
ASCII straight quotes, plain dashes, and plain dots, but your published
posts (and final HTML output) will appear with smart quotes, em-dashes,
and proper ellipses.

SmartyPants does not modify characters within ``<pre>``, ``<code>``, ``<kbd>``,
``<math>`` or ``<script>`` tag blocks. Typically, these tags are used to
display text where smart quotes and other "smart punctuation" would not be
appropriate, such as source code or example markup.


Backslash Escapes
=================

If you need to use literal straight quotes (or plain hyphens and
periods), SmartyPants accepts the following backslash escape sequences
to force non-smart punctuation. It does so by transforming the escape
sequence into a decimal-encoded HTML entity:

(FIXME:  table here.)

.. comment    It sucks that there's a disconnect between the visual layout and table markup when special characters are involved.
.. comment ======  =====  =========
.. comment Escape  Value  Character
.. comment ======  =====  =========
.. comment \\\\\\\\    &#92;  \\\\
.. comment \\\\"     &#34;  "
.. comment \\\\'     &#39;  '
.. comment \\\\.     &#46;  .
.. comment \\\\-     &#45;  \-
.. comment \\\\`     &#96;  \`
.. comment ======  =====  =========

This is useful, for example, when you want to use straight quotes as
foot and inch marks: 6'2" tall; a 17" iMac.


Algorithmic Shortcomings
============================

One situation in which quotes will get curled the wrong way is when
apostrophes are used at the start of leading contractions. For example:

``'Twas the night before Christmas.``

In the case above, SmartyPants will turn the apostrophe into an opening
single-quote, when in fact it should be a closing one. I don't think
this problem can be solved in the general case -- every word processor
I've tried gets this wrong as well. In such cases, it's best to use the
proper HTML entity for closing single-quotes (``&#8217;``) by hand.


Copyright and License
=====================

SmartyPants_ license::

	Copyright (c) 2003 John Gruber
	(http://daringfireball.net/)
	All rights reserved.

	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are
	met:

	*   Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.

	*   Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in
		the documentation and/or other materials provided with the
		distribution.

	*   Neither the name "SmartyPants" nor the names of its contributors 
		may be used to endorse or promote products derived from this
		software without specific prior written permission.

	This software is provided by the copyright holders and contributors "as
	is" and any express or implied warranties, including, but not limited
	to, the implied warranties of merchantability and fitness for a
	particular purpose are disclaimed. In no event shall the copyright
	owner or contributors be liable for any direct, indirect, incidental,
	special, exemplary, or consequential damages (including, but not
	limited to, procurement of substitute goods or services; loss of use,
	data, or profits; or business interruption) however caused and on any
	theory of liability, whether in contract, strict liability, or tort
	(including negligence or otherwise) arising in any way out of the use
	of this software, even if advised of the possibility of such damage.


smartypants.py license::

	Copyright (c) 2007 Chad Miller
	smartypants.py is a derivative work of SmartyPants.
	
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are
	met:

	*   Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.

	*   Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in
		the documentation and/or other materials provided with the
		distribution.

	This software is provided by the copyright holders and contributors "as
	is" and any express or implied warranties, including, but not limited
	to, the implied warranties of merchantability and fitness for a
	particular purpose are disclaimed. In no event shall the copyright
	owner or contributors be liable for any direct, indirect, incidental,
	special, exemplary, or consequential damages (including, but not
	limited to, procurement of substitute goods or services; loss of use,
	data, or profits; or business interruption) however caused and on any
	theory of liability, whether in contract, strict liability, or tort
	(including negligence or otherwise) arising in any way out of the use
	of this software, even if advised of the possibility of such damage.

"""
import re


RX_TAGS_TO_SKIP = re.compile(r"<(/)?(pre|code|kbd|script|math|svg)[^>]*>", re.I)


def smartyPants(text):
	skipped_tag_stack = []
	result = []
	in_pre = False
	prev_token_last_char = ""
	# This is a cheat, used to get some context
	# for one-character tokens that consist of 
	# just a quote char. What we do is remember
	# the last character of the previous text
	# token, to use as context to curl single-
	# character quote tokens correctly.
	tokens = _tokenize(text)

	for cur_token in tokens:
		if cur_token[0] == "tag":
			# Don't mess with quotes inside some tags.
			# This does not handle self <closing/> tags!
			result.append(cur_token[1])
			skip_match = RX_TAGS_TO_SKIP.match(cur_token[1])
			if skip_match is not None:
				if not skip_match.group(1):
					skipped_tag_stack.append(skip_match.group(2).lower())
					in_pre = True
				else:
					if len(skipped_tag_stack) > 0:
						if skip_match.group(2).lower() == skipped_tag_stack[-1]:
							skipped_tag_stack.pop()
						else:
							pass
							# This close doesn't match the open.  This isn't XHTML.  We should barf here.
					if len(skipped_tag_stack) == 0:
						in_pre = False
		else:
			t = cur_token[1]
			last_char = t[-1:] # Remember last char of this token before processing.
			if not in_pre:
				oldstr = t
				t = processEscapes(t)

				t = re.sub('&quot;', '"', t)
				t = educateDashes(t)
				t = educateEllipses(t)
				# Note: backticks need to be processed before quotes.
				t = educateBackticks(t)

				if t == "'":
					# Special case: single-character ' token
					if re.match("\S", prev_token_last_char):
						t = "&#8217;"
					else:
						t = "&#8216;"
				elif t == '"':
					# Special case: single-character " token
					if re.match("\S", prev_token_last_char):
						t = "&#8221;"
					else:
						t = "&#8220;"
				else:
					# Normal case:
					t = educateQuotes(t)

			prev_token_last_char = last_char
			result.append(t)

	return "".join(result)


def processEscapes(str):
	r"""
	Parameter:  String.
	Returns:    The string, with after processing the following backslash
	            escape sequences. This is useful if you want to force a "dumb"
	            quote or other character to appear.
	
	            Escape  Value
	            ------  -----
	            \\      &#92;
	            \"      &#34;
	            \'      &#39;
	            \.      &#46;
	            \-      &#45;
	            \`      &#96;
	"""
	str = re.sub(r"""\\\\""", r"""&#92;""", str)
	str = re.sub(r'''\\"''', r"""&#34;""", str)
	str = re.sub(r"""\\'""", r"""&#39;""", str)
	str = re.sub(r"""\\\.""", r"""&#46;""", str)
	str = re.sub(r"""\\-""", r"""&#45;""", str)
	str = re.sub(r"""\\`""", r"""&#96;""", str)

	return str


def _tokenize(str):
	"""
	Parameter:  String containing HTML markup.
	Returns:    Reference to an array of the tokens comprising the input
	            string. Each token is either a tag (possibly with nested,
	            tags contained therein, such as <a href="<MTFoo>">, or a
	            run of text between tags. Each element of the array is a
	            two-element array; the first is either 'tag' or 'text';
	            the second is the actual value.
	
	Based on the _tokenize() subroutine from Brad Choate's MTRegex plugin.
	    <http://www.bradchoate.com/past/mtregex.php>
	"""
	pos = 0
	length = len(str)
	tokens = []

	depth = 6
	nested_tags = "|".join(['(?:<(?:[^<>]',] * depth) + (')*>)' * depth)
	#match = r"""(?: <! ( -- .*? -- \s* )+ > ) |  # comments
	#		(?: <\? .*? \?> ) |  # directives
	#		%s  # nested tags       """ % (nested_tags,)
	tag_soup = re.compile(r"""([^<]*)(<[^>]*>)""")

	token_match = tag_soup.search(str)

	previous_end = 0
	while token_match is not None:
		if token_match.group(1):
			tokens.append(['text', token_match.group(1)])

		tokens.append(['tag', token_match.group(2)])

		previous_end = token_match.end()
		token_match = tag_soup.search(str, token_match.end())

	if previous_end < len(str):
		tokens.append(['text', str[previous_end:]])

	return tokens


def educateQuotes(str):
	"""
	Parameter:  String.
	
	Returns:	The string, with "educated" curly quote HTML entities.
	
	Example input:  "Isn't this fun?"
	Example output: &#8220;Isn&#8217;t this fun?&#8221;
	"""
	oldstr = str
	punct_class = r"""[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]"""

	# Special case if the very first character is a quote
	# followed by punctuation at a non-word-break. Close the quotes by brute force:
	str = re.sub(r"""^'(?=%s\\B)""" % (punct_class,), r"""&#8217;""", str)
	str = re.sub(r"""^"(?=%s\\B)""" % (punct_class,), r"""&#8221;""", str)

	# Special case for double sets of quotes, e.g.:
	#   <p>He said, "'Quoted' words in a larger quote."</p>
	str = re.sub(r""""'(?=\w)""", """&#8220;&#8216;""", str)
	str = re.sub(r"""'"(?=\w)""", """&#8216;&#8220;""", str)

	# Special case for decade abbreviations (the '80s):
	str = re.sub(r"""\b'(?=\d{2}s)""", r"""&#8217;""", str)

	close_class = r"""[^\ \t\r\n\[\{\(\-]"""
	dec_dashes = r"""&#8211;|&#8212;"""

	# Get most opening single quotes:
	opening_single_quotes_regex = re.compile(r"""
			(
				\s          |   # a whitespace char, or
				&nbsp;      |   # a non-breaking space entity, or
				--          |   # dashes, or
				&[mn]dash;  |   # named dash entities
				%s          |   # or decimal entities
				&\#x201[34];    # or hex
			)
			'                 # the quote
			(?=\w)            # followed by a word character
			""" % (dec_dashes,), re.VERBOSE)
	str = opening_single_quotes_regex.sub(r"""\1&#8216;""", str)

	closing_single_quotes_regex = re.compile(r"""
			(%s)
			'
			(?!\s | s\b | \d)
			""" % (close_class,), re.VERBOSE)
	str = closing_single_quotes_regex.sub(r"""\1&#8217;""", str)

	closing_single_quotes_regex = re.compile(r"""
			(%s)
			'
			(\s | s\b)
			""" % (close_class,), re.VERBOSE)
	str = closing_single_quotes_regex.sub(r"""\1&#8217;\2""", str)

	# Any remaining single quotes should be opening ones:
	str = re.sub(r"""'""", r"""&#8216;""", str)

	# Get most opening double quotes:
	opening_double_quotes_regex = re.compile(r"""
			(
				\s          |   # a whitespace char, or
				&nbsp;      |   # a non-breaking space entity, or
				--          |   # dashes, or
				&[mn]dash;  |   # named dash entities
				%s          |   # or decimal entities
				&\#x201[34];    # or hex
			)
			"                 # the quote
			(?=\w)            # followed by a word character
			""" % (dec_dashes,), re.VERBOSE)
	str = opening_double_quotes_regex.sub(r"""\1&#8220;""", str)

	# Double closing quotes:
	closing_double_quotes_regex = re.compile(r"""
			#(%s)?   # character that indicates the quote should be closing
			"
			(?=\s)
			""" % (close_class,), re.VERBOSE)
	str = closing_double_quotes_regex.sub(r"""&#8221;""", str)

	closing_double_quotes_regex = re.compile(r"""
			(%s)   # character that indicates the quote should be closing
			"
			""" % (close_class,), re.VERBOSE)
	str = closing_double_quotes_regex.sub(r"""\1&#8221;""", str)

	# Any remaining quotes should be opening ones.
	str = re.sub(r'"', r"""&#8220;""", str)

	return str


def educateBackticks(str):
	"""
	Parameter:  String.
	Returns:    The string, with ``backticks'' -style double quotes
	            translated into HTML curly quote entities.
	Example input:  ``Isn't this fun?''
	Example output: &#8220;Isn't this fun?&#8221;
	"""

	str = re.sub(r"""``""", r"""&#8220;""", str)
	str = re.sub(r"""''""", r"""&#8221;""", str)
	return str


def educateDashes(str):
	"""
	Parameter:  String.
	
	Returns:    The string, with each instance of "--" translated to
	            an em-dash HTML entity.
	"""

	str = re.sub(r"""---""", r"""&#8212;""", str) # en  (yes, backwards)
	str = re.sub(r"""--""", r"""&#8211;""", str) # em (yes, backwards)
	return str


def educateEllipses(str):
	"""
	Parameter:  String.
	Returns:    The string, with each instance of "..." translated to
	            an ellipsis HTML entity.
	
	Example input:  Huh...?
	Example output: Huh&#8230;?
	"""

	str = re.sub(r"""\.\.\.""", r"""&#8230;""", str)
	str = re.sub(r"""\. \. \.""", r"""&#8230;""", str)
	return str


def stupefyEntities(str):
	"""
	Parameter:  String.
	Returns:    The string, with each SmartyPants HTML entity translated to
	            its ASCII counterpart.

	Example input:  &#8220;Hello &#8212; world.&#8221;
	Example output: "Hello -- world."
	"""

	str = re.sub(r"""&#8211;""", r"""-""", str)  # en-dash
	str = re.sub(r"""&#8212;""", r"""--""", str) # em-dash

	str = re.sub(r"""&#8216;""", r"""'""", str)  # open single quote
	str = re.sub(r"""&#8217;""", r"""'""", str)  # close single quote

	str = re.sub(r"""&#8220;""", r'''"''', str)  # open double quote
	str = re.sub(r"""&#8221;""", r'''"''', str)  # close double quote

	str = re.sub(r"""&#8230;""", r"""...""", str)# ellipsis

	return str

