# -*- coding: utf-8 -*-
from jinja2 import Environment, DictLoader

from clay.jinja_includewith import IncludeWith


env = Environment(
    loader=DictLoader({
        'hello': 'Hello {{ what }}!',
        'sum': '{{ a }} + {{ b }} makes {{ c }}',
    }),
    extensions=['jinja2.ext.with_', IncludeWith]
)


def test_set_context():
    tmpl = env.from_string('''
        {% include "hello" with what='world' %}
        {% include "hello" with what='world' %}
    ''')
    expected = '''
        Hello world!
        Hello world!
    '''
    result = tmpl.render()
    assert result == expected


def test_overwrite_context():
    tmpl = env.from_string('''
        {% include "hello" with what='world' %}
        {% include "hello" with what='world' %}
    ''')
    expected = '''
        Hello world!
        Hello world!
    '''
    result = tmpl.render(what='you')
    assert result == expected


def test_multiple_values():
    tmpl = env.from_string('''
        {% include "sum" with a=3, b=2, c=3+2 %}
        {% include "sum" with a=3, b=2, c=3+2 %}
    ''')
    expected = '''
        3 + 2 makes 5
        3 + 2 makes 5
    '''
    result = tmpl.render()
    assert result == expected


def test_careless_formatting():
    tmpl = env.from_string('''
        {% include "sum" with a = 'Antartica', b=42,c='no sense' %}
        {% include "sum" with a='Antartica',b=42 ,c='no sense' %}
    ''')
    expected = '''
        Antartica + 42 makes no sense
        Antartica + 42 makes no sense
    '''
    result = tmpl.render()
    assert result == expected


def test_text():
    tmpl = env.from_string('''
        {% include "hello" with what='5%, er %} lalala' %}
        {% include "hello" with what='world' %}
    ''')
    expected = '''
        Hello 5%, er %} lalala!
        Hello world!
    '''
    result = tmpl.render()
    assert result == expected


def test_include_current_context():
    tmpl = env.from_string('''
        {% set a = 2 %}{% include "sum" with c=4 %}
        {% include "sum" with c=4 %}
    ''')
    expected = '''
        2 + 2 makes 4
        2 + 2 makes 4
    '''
    result = tmpl.render(b=2)
    assert result == expected


def test_unobstrusiveness():
    tmpl = env.from_string('''{% include "hello" %}''')
    r1 = tmpl.render(what='you')
    tmpl = env.from_string('''{% include "hello" with context %}''')
    r2 = tmpl.render(what='you')
    assert r1 == r2 == 'Hello you!'

