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
# 
# Each serializer method takes a `printer` argument,
# which should be a function that returns a serialized
# value for objects of builtin types.

def serialize(obj, printer=str):
    if isinstance(obj, css.Hexcolor):
        return serialize_Hexcolor(obj, printer)
    elif isinstance(obj, css.Function):
        return serialize_Function(obj, printer)
    elif isinstance(obj, css.Uri):
        return serialize_Uri(obj, printer)
    elif isinstance(obj, css.String):
        return serialize_String(obj, printer)
    elif isinstance(obj, css.Ident):
        return serialize_Ident(obj, printer)
    elif isinstance(obj, css.Term):
        return serialize_Term(obj, printer)
    elif isinstance(obj, css.Declaration):
        return serialize_Declaration(obj, printer)
    elif isinstance(obj, css.Ruleset):
        return serialize_Ruleset(obj, printer)
    elif isinstance(obj, css.Charset):
        return serialize_Charset(obj, printer)
    elif isinstance(obj, css.Page):
        return serialize_Page(obj, printer)
    elif isinstance(obj, css.Media):
        return serialize_Media(obj, printer)
    elif isinstance(obj, css.Import):
        return serialize_Import(obj, printer)
    elif isinstance(obj, css.GritInclude):
        return serialize_GritInclude(obj, printer)
    elif isinstance(obj, css.KeyframesRule):
        return serialize_KeyframesRule(obj, printer)
    elif isinstance(obj, css.KeyframeBlock):
        return serialize_KeyframeBlock(obj, printer)
    elif isinstance(obj, css.GritStatementList):
        return serialize_GritStatementList(obj, printer)
    elif isinstance(obj, css.GritDeclarationList):
        return serialize_GritDeclarationList(obj, printer)
    elif isinstance(obj, css.Stylesheet):
        return serialize_Stylesheet(obj, printer)
    else:
        return printer(obj)

def serialize_Hexcolor(obj, printer):
    return printer('#') + printer(obj.value)

def serialize_Function(obj, printer):
    s = printer(obj.name) + printer('(')
    if obj.params:
        s += printer(obj.params)
    s += printer(')')
    return s

def serialize_Uri(obj, printer):
    return printer('url(') + printer(obj.url) + printer(')')

def serialize_String(obj, printer):
    s = printer(obj.value.replace(u'"', u'\\"'))
    return printer('"') + s + printer('"')

def serialize_Ident(obj, printer):
    return printer(obj.name)

def serialize_Term(obj, printer):
    s = printer(obj.value)
    if obj.unary_operator:
        s = printer(obj.unary_operator) + s
    return s

def serialize_Declaration(obj, printer):
    s = serialize_Ident(obj.property, printer) 
    s += printer(':') + printer(obj.value)
    if obj.important:
        s += printer(' !important')
    return s

def serialize_Ruleset(obj, printer, after='\n'):
    s = serialize_Selector_group(obj.selectors, printer)
    s += serialize_Declaration_block(obj.declarations, printer)
    s += printer(after)
    return s

def serialize_Charset(obj, printer):
    return printer('@charset ') + printer(obj.encoding) + printer(';\n')

def serialize_Page(obj, printer):
    s = printer('@page')
    if obj.pseudo_page:
        s += serialize_Pseudo(obj.pseudo_page, printer)
    s += serialize_Declaration_block(obj.declarations, printer) + printer('\n')
    return s

def serialize_Media(obj, printer):
    s = printer('@media ')
    s += printer(',').join((printer(x) for x in obj.media_types))
    s += printer('{') + printer(' ').join([serialize_Ruleset(x, printer, after='') for x in obj.rulesets]) + printer('}\n')
    return s

def serialize_Import(obj, printer):
    s = printer('@import ') + serialize(obj.source, printer)
    if obj.media_types:
        s += printer(' ') + printer(',').join((printer(x) for x in obj.media_types))
    s += printer(';\n')
    return s

def serialize_GritInclude(obj, printer):
    return printer('<include src=') + serialize(obj.source, printer) + printer('>\n')

def serialize_KeyframesRule(obj, printer):
    s = printer('@-webkit-keyframes ') + serialize(obj.name, printer) + printer('{')
    s += printer(' ').join((printer(b) for b in obj.blocks))
    s += printer('}\n')
    return s

def serialize_KeyframeBlock(obj, printer):
    s = serialize_Selector_group(obj.selectors, printer)
    s += serialize_Declaration_block(obj.rulesets, printer)
    return s

def serialize_GritStatementList(obj, printer):
    s = printer('<if expr=') + printer(obj.expr) + printer('>\n')
    if obj.statements:
        s += printer('').join((serialize(x, printer) for x in obj.statements))
    s += printer('</if>\n')
    return s

def serialize_GritDeclarationList(obj, printer):
    s = printer('<if expr=') + printer(obj.expr) + printer('>')
    if obj.declarations:
        s += _serialize_Declarations(obj.declarations, printer)
    s += printer('</if>')
    return s

def serialize_Stylesheet(obj, printer):
    s = printer('')
    if obj.charset:
        s += serialize_Charset(obj.charset, printer) + printer('\n')
    if obj.imports:
        s += printer('\n').join((serialize_Import(x, printer) for x in obj.imports)) + printer('\n')
    s += printer('\n').join((serialize(x, printer) for x in obj.statements))
    return s

def serialize_Pseudo(obj, printer):
    return printer(':') + serialize_Ident(obj, printer)

def serialize_Selector_group(selectors, printer):
    return printer(',').join((printer(x) for x in selectors))

def _serialize_Declarations(declarations, printer):
    s = printer('')
    num_decls = len(declarations)
    for i, decl in enumerate(declarations):
        s += serialize(decl, printer)
        if isinstance(decl, css.Declaration) and i < num_decls - 1:
            s += printer(';')
    return s

def serialize_Declaration_block(declarations, printer):
    return printer('{') + _serialize_Declarations(declarations, printer) + printer('}')
