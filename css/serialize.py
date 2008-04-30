# -*- coding: utf-8 -*-
'''
A serializer for CSS.
'''

import css

def serialize(obj, serializer):
    if isinstance(obj, css.hexcolor):
        return serialize_hexcolor(obj, serializer)
    elif isinstance(obj, css.function):
        return serialize_function(obj, serializer)
    elif isinstance(obj, css.uri):
        return serialize_uri(obj, serializer)
    elif isinstance(obj, css.ident):
        return serialize_ident(obj, serializer)
    elif isinstance(obj, css.string):
        return serialize_string(obj, serializer)
    elif isinstance(obj, css.term):
        return serialize_term(obj, serializer)
    elif isinstance(obj, css.declaration):
        return serialize_declaration(obj, serializer)
    elif isinstance(obj, css.ruleset):
        return serialize_ruleset(obj, serializer)
    elif isinstance(obj, css.Charset):
        return serialize_Charset(obj, serializer)
    elif isinstance(obj, css.Page):
        return serialize_Page(obj, serializer)
    elif isinstance(obj, css.Media):
        return serialize_Media(obj, serializer)
    elif isinstance(obj, css.Import):
        return serialize_Import(obj, serializer)
    elif isinstance(obj, css.stylesheet):
        return serialize_stylesheet(obj, serializer)
    else:
        return serializer(obj)

def serialize_hexcolor(obj, serializer):
    return serializer('#') + serializer(obj.value)

def serialize_function(obj, serializer):
    return serializer(obj.name) + serializer('(') + serializer(obj.parameters) + serializer(')')

def serialize_uri(obj, serializer):
    return serializer('url(') + serializer(obj.url) + serializer(')')

def serialize_string(obj, serializer):
    s = serializer(obj.value.replace(u'"', u'\\"'))
    return serializer('"') + s + serializer('"')

def serialize_ident(obj, serializer):
    return serializer(obj.name)

def serialize_term(obj, serializer):
    s = serializer(obj.value)
    if obj.unary_operator:
        s = serializer(obj.unary_operator) + s
    return s

def serialize_declaration(obj, serializer):
    s = serialize_ident(obj.property, serializer) 
    s += serializer(':') + serializer(obj.value)
    if obj.important:
        s += serializer(' !important')
    return s

def serialize_ruleset(obj, serializer):
    s = serialize_selector_group(obj.selectors, serializer)
    s += serialize_declaration_block(obj.declarations, serializer)
    return s

def serialize_Charset(obj, serializer):
    return serializer('@charset ') + serializer(obj.encoding) + serializer(';')

def serialize_Page(obj, serializer):
    s = serializer('@page')
    if obj.pseudo_page:
        s += serialize_pseudo(obj.pseudo_page, serializer)
    s += serialize_declaration_block(obj.declarations, serializer)
    return s

def serialize_Media(obj, serializer):
    s = serializer('@media ')
    s += serializer(',').join((serializer(x) for x in obj.media_types))
    s += serializer('{') + serializer('\n').join([serialize_ruleset(x, serializer) for x in obj.rulesets]) + serializer('}')
    return s

def serialize_Import(obj, serializer):
    s = serializer('@import ') + serialize(obj.source, serializer)
    if obj.media_types:
        s += serializer(' ') + serializer(',').join((serializer(x) for x in obj.media_types))
    s += serializer(';')
    return s

def serialize_stylesheet(obj, serializer):
    s = serializer('')
    if obj.charset:
        s += serialize_Charset(obj.charset, serializer) + serializer('\n')
    if obj.imports:
        s += serializer('\n').join((serialize_Import(x, serializer) for x in obj.imports)) + serializer('\n')
    s += serializer('\n').join((serialize(x, serializer) for x in obj.statements))
    return s

def serialize_pseudo(obj, serializer):
    return serializer(':') + serialize_ident(obj, serializer)

def serialize_selector_group(selectors, serializer):
    return serializer(',').join((serializer(x) for x in selectors))

def serialize_declaration_block(declarations, serializer):
    return serializer('{') + serializer(';').join((serialize_declaration(x, serializer) for x in declarations)) + serializer('}')
