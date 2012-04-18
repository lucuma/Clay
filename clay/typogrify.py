# -*- coding: utf-8 -*-
"""
    # Typogrify Plus

    Typogrify without dependencies

"""
import re


# Some of the filters will ignore the text inside this tags
RX_TAGS_TO_SKIP = re.compile("<(/)?(?:pre|code|kbd|script|math|svg)[^>]*>",
    re.IGNORECASE)


def typogrify(text):
    """The super typography filter
    
    Applies the following filters: wrap_amps, widont, educate_dashes, 
    educate_ellipses, educate_quotes, wrap_caps, and initial_quotes.
    
    >>> typogrify('<h2>"Valhallen" & MM fans act obnoxiously</h2>')
    u'<h2><span class="dquo">&#8220;</span>Valhallen&#8221; <span class="amp">&amp;</span> <span class="caps">MM</span> fans act&nbsp;obnoxiously</h2>'

    """
    text = _to_unicode(text)
    text = wrap_amps(text)
    text = widont(text)

    # escapes, dashes, ellipses, quotes and caps
    text = dexter_lab(text)

    text = initial_quotes(text)
    return text


def dexter_lab(text, escapes=True, dashes=True, ellipses=True, 
        quotes=True, caps=True, DeeDee=False):
    """
    - Straight quotes ( " and ' ) into "curly" quote HTML entities.
    - Dashes (``--`` and ``---``) into em- and en-dash entities.
    - Three consecutive dots (``...`` or ``. . .``) into an ellipsis entity.
    - Wraps multiple capital letters in ``<span class="caps">`` 
    so they can be styled with CSS. 

    """
    text = _to_unicode(text)
    tokens = _tokenize(text)
    result = []
    in_skipped_tag = False 
    prev_token_last_char = ""
    
    for token in tokens:
        if token[0] == "tag":
            # Don't mess with tags.
            result.append(token[1])
            close_match = RX_TAGS_TO_SKIP.match(token[1])
            if close_match and close_match.group(1) == None:
                in_skipped_tag = True
            else:
                in_skipped_tag = False
        else:
            t1 = token[1]
            last_char = t1[-1:]

            if not in_skipped_tag:
                if escapes:
                    t1 = process_escapes(t1)
                if dashes:
                    t1 = educate_dashes(t1)
                if ellipses:
                    t1 = educate_ellipses(t1)
                if quotes:
                    t1 = re.sub('&quot;', '"', t1)
                    if t1 == "'":
                        # Special case: single-character ' token
                        if re.match("\S", prev_token_last_char):
                            t1 = "&#8217;"
                        else:
                            t1 = "&#8216;"
                    elif t1 == '"':
                        # Special case: single-character " token
                        if re.match("\S", prev_token_last_char):
                            t1 = "&#8221;"
                        else:
                            t1 = "&#8220;"
                    else:
                        # Normal case:
                        t1 = educate_quotes(t1)
                if caps:
                    t1 = _cap_finder.sub(_cap_wrapper, t1)

            prev_token_last_char = last_char
            result.append(t1)

    output = "".join(result)
    return output


_cap_finder = re.compile(r"""(
    # Group 2: Any amount of caps and digits
    (\b[A-Z\d]*
    # A cap string much at least include two caps (but they can have digits between them)
    [A-Z]\d*[A-Z]
    # Any amount of caps and digits or dumb apostsrophes
    [A-Z\d']*\b)
    # OR: Group 3: Some caps, followed by a '.' and an optional space
    | (\b[A-Z]+\.\s?
    # Followed by the same thing at least once more
    (?:[A-Z]+\.\s?)+)
    (?:\s|\b|$))
    """, re.VERBOSE)


def _cap_wrapper(matchobj):
    """This is necessary to keep dotted cap strings to pick up extra
    spaces."""
    if matchobj.group(2):
        return """<span class="caps">%s</span>""" % matchobj.group(2)
    else:
        if matchobj.group(3)[-1] == " ":
            caps = matchobj.group(3)[:-1]
            tail = ' '
        else:
            caps = matchobj.group(3)
            tail = ''
        return """<span class="caps">%s</span>%s""" % (caps, tail)


def educate_dashes(text):
    """Returns the text, with each instance of "--" translated to
    an em-dash HTML entity.

    >>> educate_dashes('The years 2001---2003')
    u'The years 2001&#8212;2003'
    >>> educate_dashes('You are the one--the only one--who offered help')
    u'You are the one&#8211;the only one&#8211;who offered help'

    """
    text = _to_unicode(text)
    text = re.sub(r"""---""", r"""&#8212;""", text) # en  (yes, backwards)
    text = re.sub(r"""--""", r"""&#8211;""", text) # em (yes, backwards)
    return text


def educate_ellipses(text):
    """Returns the text, with each instance of "..." translated to
    an ellipsis HTML entity.
    
    >>> educate_ellipses('Huh...?')
    u'Huh&#8230;?'

    """
    text = _to_unicode(text)
    text = re.sub(r"""\.\.\.""", r"""&#8230;""", text)
    text = re.sub(r"""\. \. \.""", r"""&#8230;""", text)
    return text


def educate_quotes(text):
    r"""Returns the text, with "educated" curly quote HTML entities.
    
    >>> educate_quotes('"Isn\'t this fun?"')
    u'&#8220;Isn&#8217;t this fun?&#8221;'

    """
    text = _to_unicode(text)
    punct_class = r"""[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]"""

    # Special case if the very first character is a quote
    # followed by punctuation at a non-word-break. Close the quotes by brute force:
    text = re.sub(r"""^'(?=%s\\B)""" % (punct_class,), r"""&#8217;""", text)
    text = re.sub(r"""^"(?=%s\\B)""" % (punct_class,), r"""&#8221;""", text)

    # Special case for double sets of quotes, e.g.:
    #   <p>He said, "'Quoted' words in a larger quote."</p>
    text = re.sub(r""""'(?=\w)""", """&#8220;&#8216;""", text)
    text = re.sub(r"""'"(?=\w)""", """&#8216;&#8220;""", text)

    # Special case for decade abbreviations (the '80s):
    text = re.sub(r"""\b'(?=\d{2}s)""", r"""&#8217;""", text)

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

    text = opening_single_quotes_regex.sub(r"""\1&#8216;""", text)

    closing_single_quotes_regex = re.compile(r"""
        (%s)
        '
        (?!\s | s\b | \d)
        """ % (close_class,), re.VERBOSE)

    text = closing_single_quotes_regex.sub(r"""\1&#8217;""", text)

    closing_single_quotes_regex = re.compile(r"""
        (%s)
        '
        (\s | s\b)
        """ % (close_class,), re.VERBOSE)

    text = closing_single_quotes_regex.sub(r"""\1&#8217;\2""", text)

    # Any remaining single quotes should be opening ones:
    text = re.sub(r"""'""", r"""&#8216;""", text)

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

    text = opening_double_quotes_regex.sub(r"""\1&#8220;""", text)

    # Double closing quotes:
    closing_double_quotes_regex = re.compile(r"""
        #(%s)?   # character that indicates the quote should be closing
        "
        (?=\s)
        """ % (close_class,), re.VERBOSE)

    text = closing_double_quotes_regex.sub(r"""&#8221;""", text)

    closing_double_quotes_regex = re.compile(r"""
        (%s)   # character that indicates the quote should be closing
        "
        """ % (close_class,), re.VERBOSE)

    text = closing_double_quotes_regex.sub(r"""\1&#8221;""", text)

    # Any remaining quotes should be opening ones.
    text = re.sub(r'"', r"""&#8220;""", text)

    return text


def initial_quotes(text):
    """Wraps initial quotes in ``class="dquo"`` for double quotes or  
    ``class="quo"`` for single quotes. Works in these block tags
    ``(h1-h6, p, li, dt, dd)`` and also accounts for potential opening inline
    elements ``a, em, strong, span, b, i``
    
    >>> initial_quotes('"With primes"')
    u'<span class="dquo">"</span>With primes"'
    >>> initial_quotes("'With single primes'")
    u'<span class="quo">\\'</span>With single primes\\''
    
    >>> initial_quotes('<a href="#">"With primes and a link"</a>')
    u'<a href="#"><span class="dquo">"</span>With primes and a link"</a>'
    
    >>> initial_quotes('&#8220;With smartypanted quotes&#8221;')
    u'<span class="dquo">&#8220;</span>With smartypanted quotes&#8221;'
    """
    text = _to_unicode(text)
    quote_finder = re.compile(r"""
        # start with an opening p, h1-6, li, dd, dt or the start of the string
        ((<(p|h[1-6]|li|dt|dd)[^>]*>|^)
        \s*
        # optional opening inline tags, with more optional white space for each.
        (<(a|em|span|strong|i|b)[^>]*>\s*)*)  
        # Find me a quote! (only need to find the left quotes and the primes)
        # double quotes are in group 7, singles in group 8 
        (("|&ldquo;|&\#8220;)|('|&lsquo;|&\#8216;))  
        """, re.VERBOSE)

    def _quote_wrapper(matchobj):
        if matchobj.group(7): 
            classname = "dquo"
            quote = matchobj.group(7)
        else:
            classname = "quo"
            quote = matchobj.group(8)
        return """%s<span class="%s">%s</span>""" % (
            matchobj.group(1), classname, quote)

    output = quote_finder.sub(_quote_wrapper, text)
    return output


def process_escapes(text):
    r"""Returns the string, with after processing the following backslash
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
    text = re.sub(r"""\\\\""", r"""&#92;""", text)
    text = re.sub(r'''\\"''', r"""&#34;""", text)
    text = re.sub(r"""\\'""", r"""&#39;""", text)
    text = re.sub(r"""\\\.""", r"""&#46;""", text)
    text = re.sub(r"""\\-""", r"""&#45;""", text)
    text = re.sub(r"""\\`""", r"""&#96;""", text)

    return text


def widont(text):
    """Replaces the space between the last two words in a string with ``&nbsp;``
    Works in these block tags ``(h1-h6, p, li, dd, dt)`` and also accounts for 
    potential closing inline elements ``a, em, strong, span, b, i``
    
    >>> widont('A very simple test')
    u'A very simple&nbsp;test'

    Single word items shouldn't be changed
    >>> widont('Test')
    u'Test'
    >>> widont(' Test')
    u' Test'
    >>> widont('<ul><li>Test</p></li><ul>')
    u'<ul><li>Test</p></li><ul>'
    >>> widont('<ul><li> Test</p></li><ul>')
    u'<ul><li> Test</p></li><ul>'
    
    >>> widont('<p>In a couple of paragraphs</p><p>paragraph two</p>')
    u'<p>In a couple of&nbsp;paragraphs</p><p>paragraph&nbsp;two</p>'
    
    >>> widont('<h1><a href="#">In a link inside a heading</i> </a></h1>')
    u'<h1><a href="#">In a link inside a&nbsp;heading</i> </a></h1>'
    
    >>> widont('<h1><a href="#">In a link</a> followed by other text</h1>')
    u'<h1><a href="#">In a link</a> followed by other&nbsp;text</h1>'

    Empty HTMLs shouldn't error
    >>> widont('<h1><a href="#"></a></h1>') 
    u'<h1><a href="#"></a></h1>'
    
    >>> widont('<div>Divs get no love!</div>')
    u'<div>Divs get no love!</div>'
    
    >>> widont('<pre>Neither do PREs</pre>')
    u'<pre>Neither do PREs</pre>'
    
    >>> widont('<div><p>But divs with paragraphs do!</p></div>')
    u'<div><p>But divs with paragraphs&nbsp;do!</p></div>'
    """
    text = _to_unicode(text)
    widont_finder = re.compile(r"""
        # must be proceeded by an approved inline opening or closing tag or
        # a nontag/nonspace
        ((?:</?(?:a|em|span|strong|i|b)[^>]*>)|[^<>\s])
        # the space to replace
        \s+
        # must be followed by non-tag non-space characters                                       
        ([^<>\s]+
        \s*
        # optional closing inline tags with optional white space after each
        (</(a|em|span|strong|i|b)>\s*)*
        # end with a closing p, h1-6, li or the end of the string
        ((</(p|h[1-6]|li|dt|dd)>)|$))
        """, re.VERBOSE)
    output = widont_finder.sub(r'\1&nbsp;\2', text)
    return output


def wrap_amps(text):
    """Wraps apersands in HTML with ``<span class="amp">`` so they can be
    styled with CSS. Apersands are also normalized to ``&amp;``. Requires 
    ampersands to have whitespace or an ``&nbsp;`` on both sides.
    
    >>> wrap_amps('One & two')
    u'One <span class="amp">&amp;</span> two'
    >>> wrap_amps('One &amp; two')
    u'One <span class="amp">&amp;</span> two'
    >>> wrap_amps('One &#38; two')
    u'One <span class="amp">&amp;</span> two'

    >>> wrap_amps('One&nbsp;&amp;&nbsp;two')
    u'One&nbsp;<span class="amp">&amp;</span>&nbsp;two'

    It won't mess up & that are already wrapped, in entities or URLs

    >>> wrap_amps('One <span class="amp">&amp;</span> two')
    u'One <span class="amp">&amp;</span> two'
    >>> wrap_amps('&ldquo;this&rdquo; & <a href="/?that&amp;test">that</a>')
    u'&ldquo;this&rdquo; <span class="amp">&amp;</span> <a href="/?that&amp;test">that</a>'

    It should ignore standalone amps that are in attributes
    >>> wrap_amps('<link href="xyz.html" title="One & Two">xyz</link>')
    u'<link href="xyz.html" title="One & Two">xyz</link>'

    """
    text = _to_unicode(text)
    # tag_pattern from
    # http://haacked.com/archive/2004/10/25/usingregularexpressionstomatchhtml.aspx
    # it kinda sucks but it fixes the standalone amps in attributes bug
    tag_pattern = '</?\w+((\s+\w+(\s*=\s*(?:".*?"|\'.*?\'|[^\'">\s]+))?)+\s*|\s*)/?>'
    amp_finder = re.compile(r"(\s|&nbsp;)(&|&amp;|&\#38;)(\s|&nbsp;)")
    intra_tag_finder = re.compile(r'(?P<prefix>(%s)?)(?P<text>([^<]*))(?P<suffix>(%s)?)' % (tag_pattern, tag_pattern))

    def _amp_process(groups):
        prefix = groups.group('prefix') or ''
        text = amp_finder.sub(r"""\1<span class="amp">&amp;</span>\3""", groups.group('text'))
        suffix = groups.group('suffix') or ''
        return prefix + text + suffix

    output = intra_tag_finder.sub(_amp_process, text)
    return output


def wrap_caps(text):
    r"""Wraps multiple capital letters in ``<span class="caps">`` 
    so they can be styled with CSS. 
    
    >>> wrap_caps("A message from KU")
    u'A message from <span class="caps">KU</span>'
    
    >>> wrap_caps("<PRE>CAPS</pre> more CAPS")
    u'<PRE>CAPS</pre> more <span class="caps">CAPS</span>'

    >>> wrap_caps("A message from 2KU2 with digits")
    u'A message from <span class="caps">2KU2</span> with digits'
    
    Dotted caps followed by spaces should never include them in the wrap
    >>> wrap_caps("wrap D.O.T.   like so.")
    u'wrap <span class="caps">D.O.T.</span>  like so.'

    All caps with with apostrophes in them shouldn't break. Only handles
    dump apostrophes though.
    >>> wrap_caps("JIMMY'S")
    u'<span class="caps">JIMMY\'S</span>'

    >>> wrap_caps("<i>D.O.T.</i>HE34T<b>RFID</b>")
    u'<i><span class="caps">D.O.T.</span></i><span class="caps">HE34T</span><b><span class="caps">RFID</span></b>'
    """
    text = _to_unicode(text)
    return dexter_lab(text, escapes=False, dashes=False, ellipses=False, 
        quotes=False, caps=True)


# UTILS ---------------------------------------------------------------------

def _is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    to_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def _to_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.

    If strings_only is True, don't convert (some) non-string-like objects.

    --------------------------------
    Copied almost unchanged from Django <https://www.djangoproject.com/>
    Copyright © 2005-2011 Django Software Foundation.
    Used under the modified BSD license.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode.
    if isinstance(s, unicode):
        return s
    if strings_only and _is_protected_type(s):
        return s
    encoding = encoding or 'utf-8'
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = u' '.join([to_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
    return s


def _tokenize(text):
    """Takes a text containing HTML markup and returns a reference to an 
    array of the tokens comprising the input string.

    Each token is either a tag (possibly with nested, tags contained therein,
    such as <a href="<MTFoo>">, or a run of text between tags.

    Each element of the array is a two-element array; the first is either 
    'tag' or 'text'; the second is the actual value.
    
    Based on the _tokenize() subroutine from Brad Choate's MTRegex plugin.
        <http://www.bradchoate.com/past/mtregex.php>
    """
    pos = 0
    length = len(text)
    tokens = []

    depth = 6
    nested_tags = "|".join(['(?:<(?:[^<>]',] * depth) + (')*>)' * depth)
    #match = r"""(?: <! ( -- .*? -- \s* )+ > ) |  # comments
    #       (?: <\? .*? \?> ) |  # directives
    #       %s  # nested tags       """ % (nested_tags,)
    tag_soup = re.compile(r"""([^<]*)(<[^>]*>)""")

    token_match = tag_soup.search(text)

    previous_end = 0
    while token_match is not None:
        if token_match.group(1):
            tokens.append(['text', token_match.group(1)])

        tokens.append(['tag', token_match.group(2)])

        previous_end = token_match.end()
        token_match = tag_soup.search(text, token_match.end())

    if previous_end < len(text):
        tokens.append(['text', text[previous_end:]])

    return tokens


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()

