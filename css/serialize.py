# -*- coding: utf-8 -*-
'''
A serializer for CSS.
'''

import css

# This module comprises all serialization code for the
# syntax object of CSS, kept here so that the serialization
# strategy for the whole system can be modified easily
# without the need to touch a dozen classes.  
#
# Adding a
# new type of data requires another conditional in
# serialize(), and possibly a new serialize_<type>()
# method.  (The data types of CSS are finite and the number
# relatively small, so this should be a rare occassion.)

def serialize(obj, serializer):
    if isinstance(obj, css.Hexcolor):
        return serialize_Hexcolor(obj, serializer)
    elif isinstance(obj, css.Function):
        return serialize_Function(obj, serializer)
    elif isinstance(obj, css.Uri):
        return serialize_Uri(obj, serializer)
    elif isinstance(obj, css.String):
        return serialize_String(obj, serializer)
    elif isinstance(obj, css.Ident):
        return serialize_Ident(obj, serializer)
    elif isinstance(obj, css.Term):
        return serialize_Term(obj, serializer)
    elif isinstance(obj, css.Declaration):
        return serialize_Declaration(obj, serializer)
    elif isinstance(obj, css.Ruleset):
        return serialize_Ruleset(obj, serializer)
    elif isinstance(obj, css.Charset):
        return serialize_Charset(obj, serializer)
    elif isinstance(obj, css.Page):
        return serialize_Page(obj, serializer)
    elif isinstance(obj, css.Media):
        return serialize_Media(obj, serializer)
    elif isinstance(obj, css.Import):
        return serialize_Import(obj, serializer)
    elif isinstance(obj, css.Stylesheet):
        return serialize_Stylesheet(obj, serializer)
    else:
        return serializer(obj)

def serialize_Hexcolor(obj, serializer):
    return serializer('#') + serializer(obj.value)

def serialize_Function(obj, serializer):
    return serializer(obj.name) + serializer('(') + serializer(obj.parameters) + serializer(')')

def serialize_Uri(obj, serializer):
    return serializer('url(') + serializer(obj.url) + serializer(')')

def serialize_String(obj, serializer):
    s = serializer(obj.value.replace(u'"', u'\\"'))
    return serializer('"') + s + serializer('"')

def serialize_Ident(obj, serializer):
    return serializer(obj.name)

def serialize_Term(obj, serializer):
    s = serializer(obj.value)
    if obj.unary_operator:
        s = serializer(obj.unary_operator) + s
    return s

def serialize_Declaration(obj, serializer):
    s = serialize_Ident(obj.property, serializer) 
    s += serializer(':') + serializer(obj.value)
    if obj.important:
        s += serializer(' !important')
    return s

def serialize_Ruleset(obj, serializer):
    s = serialize_Selector_group(obj.selectors, serializer)
    s += serialize_Declaration_block(obj.declarations, serializer)
    return s

def serialize_Charset(obj, serializer):
    return serializer('@charset ') + serializer(obj.encoding) + serializer(';')

def serialize_Page(obj, serializer):
    s = serializer('@page')
    if obj.pseudo_page:
        s += serialize_Pseudo(obj.pseudo_page, serializer)
    s += serialize_Declaration_block(obj.declarations, serializer)
    return s

def serialize_Media(obj, serializer):
    s = serializer('@media ')
    s += serializer(',').join((serializer(x) for x in obj.media_types))
    s += serializer('{') + serializer('\n').join([serialize_Ruleset(x, serializer) for x in obj.rulesets]) + serializer('}')
    return s

def serialize_Import(obj, serializer):
    s = serializer('@import ') + serialize(obj.source, serializer)
    if obj.media_types:
        s += serializer(' ') + serializer(',').join((serializer(x) for x in obj.media_types))
    s += serializer(';')
    return s

def serialize_Stylesheet(obj, serializer):
    s = serializer('')
    if obj.charset:
        s += serialize_Charset(obj.charset, serializer) + serializer('\n')
    if obj.imports:
        s += serializer('\n').join((serialize_Import(x, serializer) for x in obj.imports)) + serializer('\n')
    s += serializer('\n').join((serialize(x, serializer) for x in obj.statements))
    return s

def serialize_Pseudo(obj, serializer):
    return serializer(':') + serialize_Ident(obj, serializer)

def serialize_Selector_group(selectors, serializer):
    return serializer(',').join((serializer(x) for x in selectors))

def serialize_Declaration_block(declarations, serializer):
    return serializer('{') + serializer(';').join((serialize_Declaration(x, serializer) for x in declarations)) + serializer('}')
