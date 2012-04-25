# -*- coding: utf-8 -*-
'''
A parser for CSS.
'''


import re
from ply import yacc as ply_yacc
from csslex import csslexer
import css


__all__ = ('cssparser', 'yacc')


def normalize(x):
    '''Normalizes escaped characters to their literal value.'''
    p = ur'\\0{0,4}([0-9]{2})'
    r = lambda m: chr(int(m.groups()[0],16))
    return re.sub(p,r,x).lower()


def URI_value(x):
    url = normalize(x)[4:-1].strip()
    if -1 != '"\''.find(url[0]):
        url = STRING_value(url)
    return css.Uri(url)


def STRING_value(x):
    q = x[0]
    return css.String(x[1:-1].replace(u'\\'+q,q))


class cssparser(object):
    tokens = csslexer.tokens

    def p_stylesheet(self, p):
        '''
        stylesheet : charset spaces_or_sgml_comments imports statements
                   | spaces_or_sgml_comments imports statements
        '''
        if isinstance(p[1], css.Charset):
            p[0] = css.Stylesheet(p[4], p[3], p[1])
        else:
            p[0] = css.Stylesheet(p[3], p[2])

    def p_charset(self, p):
        '''
        charset : CHARSET_SYM STRING ';'
        '''
        p[0] = css.Charset(STRING_value(p[2]))

    def p_media(self, p):
        '''
        media : MEDIA_SYM spaces media_types LBRACE spaces rulesets '}' spaces
        '''
        p[0] = css.Media(p[3], p[6])

    def p_medium(self, p):
        '''
        medium : IDENT spaces
        '''
        p[0] = p[1]

    def p_page(self, p):
        '''
        page : PAGE_SYM spaces pseudo_page spaces LBRACE block_declarations '}' spaces
             | PAGE_SYM spaces LBRACE block_declarations '}' spaces
        '''
        if isinstance(p[3], css.Ident):
            p[0] = css.Page(p[6], p[3])
        else:
            p[0] = css.Page(p[4])

    def p_pseudo_page(self, p):
        '''
        pseudo_page : ':' IDENT
        '''
        p[0] = css.Ident(p[2])

    def p_import(self, p):
        '''
        import : IMPORT_SYM spaces import_source media_types spaces ';' spaces
               | IMPORT_SYM spaces import_source ';' spaces
        '''
        if isinstance(p[4], list):
            p[0] = css.Import(p[3], p[4])
        else:
            p[0] = css.Import(p[3])

    def p_keyframes_rule(self, p):
        '''
        keyframes_rule : KEYFRAMES_SYM spaces IDENT spaces LBRACE spaces keyframes_blocks '}' spaces
        '''
        p[0] = css.KeyframesRule(p[3], p[7])

    def p_operator(self, p):
        '''
        operator : '/' spaces
                 | COMMA spaces
                 | empty
        '''
        p[0] = p[1]

    def p_combinator(self, p):
        '''
        combinator : PLUS spaces
                   | GREATER spaces
                   | TILDE spaces
                   | spaces
        '''
        p[0] = p[1]

    def p_unary_operator(self, p):
        '''
        unary_operator : '-' 
                       | PLUS
        '''
        p[0] = p[1]

    def p_property(self, p):
        '''
        property : IDENT spaces
        '''
        p[0] = css.Ident(p[1])

    def p_ruleset(self, p):
        '''
        ruleset : selectors_group LBRACE spaces block_declarations '}' spaces
        '''
        p[0] = css.Ruleset(p[1], p[4])

    def p_selector(self, p):
        '''
        selector : simple_selector_sequence simple_selectors
        '''
        p[0] = u''.join(p[1:])

    def p_simple_selector_sequence(self, p):
        '''
        simple_selector_sequence : type_selector simple_selector_components
                                 | universal simple_selector_components
                                 | simple_selector_component simple_selector_components
        '''
        p[0] = u''.join(p[1:])

    def p_type_selector(self, p):
        '''
        type_selector : namespace_prefix element_name
                      | element_name
        '''
        p[0] = u''.join(p[1:])

    def p_universal(self, p):
        '''
        universal : namespace_prefix '*'
                  | '*'
        '''
        p[0] = u''.join(p[1:])

    def p_namespace_prefix(self, p):
        '''
        namespace_prefix : IDENT '|'
                         | '*' '|'
                         | '|'
        '''
        p[0] = u''.join(p[1:])

    def p_simple_selectors(self, p):
        '''
        simple_selectors : combinator simple_selector_sequence simple_selectors
                         | empty
        '''
        p[0] = u''.join(p[1:])


    def p_simple_selector_component(self, p):
        '''
        simple_selector_component : HASH
                                  | class
                                  | attrib
                                  | pseudo
                                  | negation
        '''
        p[0] = p[1]

    def p_simple_selector_components(self, p):
        '''
        simple_selector_components : simple_selector_component simple_selector_components
                                   | empty
        '''
        p[0] = u''.join(p[1:])

    def p_class(self, p):
        '''
        class : '.' IDENT
        '''
        p[0] = u''.join(p[1:])

    def p_element_name(self, p):
        '''
        element_name : IDENT
        '''
        p[0] = p[1]

    def p_attrib(self, p):
        '''
        attrib : '[' spaces namespace_prefix IDENT spaces attrib_match ']'
               | '[' spaces IDENT spaces attrib_match ']'
        '''
        p[0] = u''.join(p[1:])

    def p_pseudo(self, p):
        '''
        pseudo : pseudo_colons IDENT
               | pseudo_colons functional_pseudo
        '''
        p[0] = u''.join(p[1:])

    def p_pseudo_colons(self, p):
        '''
        pseudo_colons : ':' ':'
                      | ':'
        '''
        p[0] = u''.join(p[1:])

    def p_functional_pseudo(self, p):
        '''
        functional_pseudo : FUNCTION spaces expressions spaces ')'
        '''
        p[0] = u''.join(p[1:])

    def p_expressions(self, p):
        '''
        expressions : expressions spaces expression
                    | expression
        '''
        if len(p) == 2:
          p[0] = [p[1]]
        else:
          p[0] = p[1]
          p[0].append(p[3])

    # NOTE: These are part of a selector, whereas expr is part of a value of a rule.
    def p_expression(self, p):
        '''
        expression : PLUS
                   | '-'
                   | DIMENSION
                   | NUMBER
                   | STRING
                   | IDENT
        '''
        p[0] = p[1]

    def p_negation(self, p):
        '''
        negation : NOT spaces negation_arg spaces ')'
        '''
        p[0] = u''.join(p[1:])

    def p_negation_arg(self, p):
        '''
        negation_arg : type_selector
                     | universal
                     | HASH
                     | class
                     | attrib
                     | pseudo
        '''
        p[0] = p[1]

    def p_declaration(self, p):
        '''
        declaration : property ':' spaces expr prio
                    | property ':' spaces expr
                    | empty
        '''
        if len(p) == 2:
            p[0] = None
        else:
            important = len(p) == 6
            p[0] = css.Declaration(p[1], p[4], important)

    def p_prio(self, p):
        '''
        prio : IMPORTANT_SYM spaces
        '''
        p[0] = p[1]

    def p_expr(self, p):
        '''
        expr : expr operator term
             | expr term
             | term
        '''
        if len(p) == 4:
            p[0] = u''.join([unicode(x) for x in p[1:]])
        elif len(p) == 3:
            p[0] = unicode(p[1]) + u' ' + unicode(p[2])
        else:
            p[0] = p[1]
    
    def p_term(self, p):
        '''
        term : unary_operator term_quant
             | term_quant
             | STRING spaces
             | IDENT spaces
             | URI spaces
             | hexcolor
             | function
        '''
        if isinstance(p[1], css.Function) or isinstance(p[1], css.Hexcolor):
            p[0] = p[1]
        elif p.slice[1].type == 'URI':
            p[0] = URI_value(p[1])
        elif p.slice[1].type == 'STRING':
            p[0] = STRING_value(p[1])
        elif p.slice[1].type == 'IDENT':
            p[0] = css.Ident(p[1])            
        elif -1 != '-+'.find(p[1]):
            p[0] = css.Term(p[2], p[1])
        else:
            p[0] = css.Term(p[1])
    
    def p_term_quant(self, p):
        '''
        term_quant : NUMBER spaces
                   | PERCENTAGE spaces
                   | LENGTH spaces
                   | EMS spaces
                   | EXS spaces
                   | ANGLE spaces
                   | TIME spaces
                   | FREQ spaces
        '''
        p[0] = normalize(p[1])

    def p_function(self, p):
        '''
        function : FUNCTION spaces expr ')' spaces
        '''
        name = p[1][:-1] # strip the open paren
        p[0] = css.Function(name, p[3])

    def p_hexcolor(self, p):
        '''
        hexcolor : HASH spaces
        '''
        p[0] = css.Hexcolor(p[1])

    def p_spaces(self, p):
        '''
        spaces : spaces S
               | S
               | empty
        '''
        p[0] = p[1] and u' '

    def p_imports(self, p):
        '''
        imports : imports import spaces_or_sgml_comments
                | import spaces_or_sgml_comments
                | empty
        '''
        if not p[1]:
            p[0] = []
        elif isinstance(p[1], list):
            p[0] = p[1]
            p[0].append(p[2])
        else:
            p[0] = [p[1]]

    def p_statements(self, p):
        '''
        statements : statements ruleset spaces_or_sgml_comments
                   | statements media spaces_or_sgml_comments
                   | statements page spaces_or_sgml_comments
                   | statements keyframes_rule spaces_or_sgml_comments
                   | ruleset spaces_or_sgml_comments
                   | media spaces_or_sgml_comments
                   | page spaces_or_sgml_comments
                   | keyframes_rule spaces_or_sgml_comments
                   | empty
        '''
        if not p[1]:
            p[0] = []
        elif isinstance(p[1], list):
            p[0] = p[1]
            p[0].append(p[2])
        else:
            p[0] = [p[1]]

    def p_import_source(self, p):
        '''
        import_source : STRING spaces
                      | URI spaces
        '''
        if p.slice[1].type == 'URI':
            p[0] = URI_value(p[1])
        else:
            p[0] = STRING_value(p[1])

    def p_media_types(self, p):
        '''
        media_types : media_types COMMA spaces medium
                    | medium
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[4])

    def p_keyframes_blocks(self, p):
        '''
        keyframes_blocks : keyframes_blocks spaces keyframes_block
                         | keyframes_block
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[3])

    def p_keyframes_block(self, p):
        '''
        keyframes_block : keyframe_selectors LBRACE spaces block_declarations '}' spaces
        '''
        b = p[4] or list()
        if isinstance(p[1], list):
            p[0] = css.KeyframeBlock(p[1], b)
        else:
            p[0] = css.KeyframeBlock([p[1]], b)

    def p_keyframe_selectors(self, p):
        '''
        keyframe_selectors : keyframe_selectors COMMA spaces keyframe_selector
                           | keyframe_selector
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[4])

    def p_keyframe_selector(self, p):
        '''
        keyframe_selector : FROM_SYM spaces
                          | TO_SYM spaces
                          | PERCENTAGE spaces
        '''
        p[0] = p[1]

    def p_rulesets(self, p):
        '''
        rulesets : rulesets ruleset
                 | ruleset
                 | empty
        '''
        if not p[1]:
            p[0] = []
        elif isinstance(p[1], list):
            p[0] = p[1]
            p[0].append(p[2])
        else:
            p[0] = [p[1]]

    def p_selectors_group(self, p):
        '''
        selectors_group : selectors_group COMMA spaces selector
                        | selector
        '''
        if len(p) == 2:
            p[0] = p[1:]
        else:
            p[0] = p[1] + p[4:]

    def p_block_declarations(self, p):
        '''
        block_declarations : block_declarations ';' spaces declaration
                           | declaration
        '''
        if len(p) == 2:
            p[0] = []
            if p[1]:
                p[0].append(p[1])
        else:
            p[0] = p[1]
            if p[4]:
                p[0].append(p[4])

    def p_attrib_match(self, p):
        '''
        attrib_match : attrib_op spaces attrib_val spaces
                     | empty
        '''
        p[0] = u''.join(p[1:])

    def p_attrib_op(self, p):
        '''
        attrib_op : PREFIXMATCH
                  | SUFFIXMATCH
                  | SUBSTRINGMATCH
                  | '='
                  | INCLUDES
                  | DASHMATCH
        '''
        p[0] = p[1]

    def p_attrib_val(self, p):
        '''
        attrib_val : IDENT
                   | STRING
        '''
        p[0] = p[1]

    def p_spaces_or_sgml_comments(self, p):
        '''
        spaces_or_sgml_comments : spaces_or_sgml_comments S
                                | spaces_or_sgml_comments CDO
                                | spaces_or_sgml_comments CDC
                                | S
                                | CDO
                                | CDC
                                | empty
        '''
        p[0] = p[1] and u' '

    def p_empty(self, p):
        '''
        empty :
        '''
        p[0] = u''

    def p_error(self, p):
        print "Syntax error at '%r'" % (p,)


def yacc(**kw):
    kw['module'] = cssparser()
    if 'start' not in kw:
        kw['start'] = 'stylesheet'
    return ply_yacc.yacc(**kw)
