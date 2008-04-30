# -*- coding: utf-8 -*-
'''
A parser for CSS.
'''

import re
from ply import yacc as _yacc
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

def IDENT_value(x):
    return css.Ident(x)

class cssparser(object):
    tokens = csslexer.tokens
    
    def p_stylesheet(self, p):
        '''
        stylesheet : S stylesheet
                   | charset stylesheet2
                   | stylesheet2
        '''
        if len(p) == 3:
            if p.slice[1].type == 'S':
                p[0] = p[2]
            else:
                p[0] = css.Stylesheet(p[2].statements, p[2].imports, charset=p[1])
        else:
            p[0] = p[1]
    
    def p_charset(self, p):
        '''
        charset : CHARSET_SYM STRING ';'
        '''
        p[0] = css.Charset(STRING_value(p[2]))
    
    def p_stylesheet2(self, p):
        '''
        stylesheet2 : S stylesheet2
                    | CDO stylesheet2
                    | CDC stylesheet2
                    | import stylesheet2
                    | stylesheet3
        '''
        imports = list()
        if len(p) == 3:
            statements = p[2]
            if isinstance(p[1], css.Import):
                imports.append(p[1])
        else:
            statements = p[1]
        
        if isinstance(statements, css.Stylesheet):
            imports.extend(statements.imports)
            statements = statements.statements
        
        p[0] = css.Stylesheet(statements, imports)
    
    def p_stylesheet3(self, p):
        '''
        stylesheet3 : S stylesheet3
                    | CDO stylesheet3
                    | CDC stylesheet3
                    | ruleset stylesheet3
                    | media stylesheet3
                    | page stylesheet3
                    |
        '''
        p[0] = list()
        if len(p) == 3:
            if (isinstance(p[1], css.Ruleset) 
                or isinstance(p[1], css.Media)
                or isinstance(p[1], css.Page)):
                p[0].append(p[1])
 
            p[0].extend(p[2])
    
    def p_media(self, p):
        '''
        media : MEDIA_SYM S media2
              | MEDIA_SYM media2
        '''
        if len(p) == 4:
            p[0] = p[3]
        else:
            p[0] = p[2]
    
    def p_media2(self, p):
        '''
        media2 : medium S media3
               | medium media3
        '''
        media_types = [ p[1] ]
        
        if len(p) == 4:
            rulesets = p[3]
        else:
            rulesets = p[2]
        
        if isinstance(rulesets, css.Media):
            media_types.extend(rulesets.media_types)
            rulesets = rulesets.rulesets
        
        p[0] = css.Media(media_types, rulesets)
    
    def p_media3(self, p):
        '''
        media3 : COMMA S media2
               | COMMA media2
               | media4
        '''
        if p[1] == ',':
            if len(p) == 4:
                p[0] = p[3]
            else:
                p[0] = p[2]
        else:
            p[0] = p[1]
    
    def p_media4(self, p):
        '''
        media4 : LBRACE S media5
               | LBRACE media5
        '''
        if len(p) == 4:
            p[0] = p[3]
        else:
            p[0] = p[2]
    
    def p_media5(self, p):
        '''
        media5 : ruleset media5
               | ruleset media_x
        '''
        p[0] = [ p[1] ]
        if p[2]:
            p[0].extend(p[2])
    
    def p_media_x(self, p):
        '''
        media_x : '}' S
                | '}'
        '''
        pass
    
    def p_medium(self, p):
        '''
        medium : IDENT S
               | IDENT
        '''
        p[0] = IDENT_value(p[1])
    
    def p_page(self, p):
        '''
        page : PAGE_SYM S page2
             | PAGE_SYM page2
        '''
        if len(p) == 4:
            p[0] = p[3]
        else:
            p[0] = p[2]
    
    def p_page2(self, p):
        '''
        page2 : pseudo_page S page3
              | pseudo_page page3
              | page3
        '''
        if len(p) == 4:
            p[0] = css.Page(p[3].declarations, p[1])
        elif len(p) == 3:
            p[0] = css.Page(p[2].declarations, p[1])
        else:
            p[0] = p[1]
    
    def p_page3(self, p):
        '''
        page3 : LBRACE S page4
              | LBRACE page4
        '''
        if len(p) == 4:
            p[0] = css.Page(p[3])
        else:
            p[0] = css.Page(p[2])
    
    def p_page4(self, p):
        '''
        page4 : declaration S page5
              | declaration page5
              | S page_x
              | page_x
        '''
        p[0] = list()
        if isinstance(p[1], css.Declaration):
            p[0].append(p[1])
            
            if len(p) == 4:
                p[0].extend(p[3])
            else:
                p[0].extend(p[2])
    
    def p_page5(self, p):
        '''
        page5 : ';' S page4
              | ';' page4
              | page_x
        '''
        if p[1] == ';':
            if len(p) == 4:
                p[0] = p[3]
            else:
                p[0] = p[2]
        else:
            p[0] = list()
    
    def p_page_x(self, p):
        '''
        page_x : '}' S
               | '}'
        '''
        pass
    
    def p_pseudo_page(self, p):
        '''
        pseudo_page : ':' IDENT
        '''
        p[0] = IDENT_value(p[2])
    
    def p_import(self, p):
        '''
        import : IMPORT_SYM S import2
               | IMPORT_SYM import2
        '''
        if len(p) == 4:
            p[0] = p[3]
        else:
            p[0] = [2]
    
    def p_import2(self, p):
        '''
        import2 : STRING S import3
                | STRING import3
                | URI S import3
                | URI import3
        '''
        if p.slice[1].type == 'URI':
            source = URI_value(p[1])
        else:
            source = STRING_value(p[1])
        
        if len(p) == 4:
            media_types = p[3]
        else:
            media_types = p[2]
        
        p[0] = css.Import(source, media_types)
    
    def p_import3(self, p):
        '''
        import3 : medium S import4
                | medium import4
                | import_x
        '''
        p[0] = list()
        if p[1]:
            p[0].append(p[1])
        
        if len(p) == 4:
            p[0].extend(p[3])
        elif len(p) == 3:
            p[0].extend(p[2])
    
    def p_import4(self, p):
        '''
        import4 : COMMA S import3
                | COMMA import3
                | import_x
        '''
        if p[1] == ',':
            if len(p) == 4:
                p[0] = p[3]
            else:
                p[0] = p[2]
    
    def p_import_x(self, p):
        '''
        import_x : ';' S
                 | ';'
        '''
        pass
    
    def p_operator(self, p):
        '''
        operator : '/' S
                 | '/'
                 | COMMA S
                 | COMMA
        '''
        p[0] = p[1]
    
    def p_combinator(self, p):
        '''
        combinator : PLUS S
                   | PLUS
                   | GREATER S
                   | GREATER
                   | S
        '''
        p[0] = p[1].strip() or p[1]
    
    def p_unary_operator(self, p):
        '''
        unary_operator : '-'
                       | PLUS
        '''
        p[0] = p[1]
    
    def p_property(self, p):
        '''
        property : IDENT S
                 | IDENT 
        '''
        p[0] = IDENT_value(p[1])
    
    def p_ruleset(self, p):
        '''
        ruleset : selector S ruleset2
                | selector ruleset2
        '''
        if len(p) == 4:
            declarations = p[3]
        else:
            declarations = p[2]
        
        selectors = [ p[1] ]
        
        if isinstance(declarations, css.Ruleset):
            selectors.extend(declarations.selectors)
            declarations = declarations.declarations
            
        p[0] = css.Ruleset(selectors, declarations)
    
    def p_ruleset2(self, p):
        '''
        ruleset2 : COMMA S ruleset
                 | COMMA ruleset
                 | ruleset3
        '''
        if p[1] == ',':
            if len(p) == 4:
                p[0] = p[3]
            else:
                p[0] = p[2]
        else:
            p[0] = p[1]
    
    def p_ruleset3(self, p):
        '''
        ruleset3 : LBRACE S ruleset4
                 | LBRACE ruleset4
        '''
        if len(p) == 4:
            p[0] = p[3]
        else:
            p[0] = p[2]
    
    def p_ruleset4(self, p):
        '''
        ruleset4 : declaration S ruleset5
                 | declaration ruleset5
                 | S ruleset_x
                 | ruleset_x
        '''
        p[0] = list()
        if isinstance(p[1], css.Declaration):
            p[0].append(p[1])
            
            if len(p) == 4:
                p[0].extend(p[3])
            else:
                p[0].extend(p[2])
    
    def p_ruleset5(self, p):
        '''
        ruleset5 : ';' S ruleset4
                 | ';' ruleset4
                 | ruleset_x
        '''
        if p[1] == ';':
           if len(p) == 4:
               p[0] = p[3]
           else:
               p[0] = p[2]
        else:
            p[0] = list()
    
    def p_ruleset_x(self, p):
        '''
        ruleset_x : '}' S
                  | '}'
        '''
        pass
    
    def p_selector(self, p):
        '''
        selector : simple_selector selector2
                 | simple_selector
        '''
        p[0] = u''.join(p[1:])
    
    def p_selector2(self, p):
        '''
        selector2 : combinator selector
        '''
        p[0] = u''.join(p[1:])
    
    def p_simple_selector(self, p):
        '''
        simple_selector : element_name simple_selector2
                        | element_name
                        | simple_selector2
        '''
        p[0] = u''.join(p[1:])
    
    def p_simple_selector2(self, p):
        '''
        simple_selector2 : HASH simple_selector2
                         | HASH
                         | class simple_selector2
                         | class
                         | attrib simple_selector2
                         | attrib
                         | pseudo simple_selector2
                         | pseudo
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
                     | '*'
        '''
        p[0] = p[1]
    
    def p_attrib(self, p):
        '''
        attrib : '[' S attrib2 ']'
               | '[' attrib2 ']'
        '''
        p[0] = u''.join(p[1:])
    
    def p_attrib2(self, p):
        '''
        attrib2 : IDENT S attrib3
                | IDENT attrib3
                | IDENT S
                | IDENT
        '''
        p[0] = u''.join(p[1:])
    
    def p_attrib3(self, p):
        '''
        attrib3 : '=' S attrib4
                | '=' attrib4
                | INCLUDES S attrib4
                | INCLUDES attrib4
                | DASHMATCH S attrib4
                | DASHMATCH attrib4
        '''
        p[0] = u''.join(p[1:])
    
    def p_attrib4(self, p):
        '''
        attrib4 : IDENT S
                | IDENT
                | STRING S
                | STRING
        '''
        p[0] = u''.join(p[1:])
    
    def p_pseudo(self, p):
        '''
        pseudo : ':' IDENT
               | ':' FUNCTION S pseudo2
               | ':' FUNCTION pseudo2
        '''
        p[0] = u''.join(p[1:])
    
    def p_pseudo2(self, p):
        '''
        pseudo2 : IDENT S ')'
                | IDENT ')'
                | ')'
        '''
        p[0] = u''.join(p[1:])
    
    def p_declaration(self, p):
        '''
        declaration : property ':' S declaration2
                    | property ':' declaration2
        '''
        if len(p) == 5:
            value, important = p[4][0], 2 == len(p[4])
        else:
            value, important = p[3][0], 2 == len(p[3])
        
        p[0] = css.Declaration(p[1],value,important)
    
    def p_declaration2(self, p):
        '''
        declaration2 : expr prio
                     | expr
        '''
        p[0] = p[1:]
    
    def p_prio(self, p):
        '''
        prio : IMPORTANT_SYM S
             | IMPORTANT_SYM
        '''
        p[0] = p[1]
    
    def p_expr(self, p):
        '''
        expr : term operator expr
             | term expr
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
             | STRING S
             | STRING
             | IDENT S
             | IDENT
             | URI S
             | URI
             | hexcolor
             | function
        '''
        if len(p) == 3 and -1 != '-+'.find(p[1]):
            p[0] = css.Term(p[2],p[1])
        else:
            t, val = p.slice[1], p[1]

            if isinstance(val, css.Function) or isinstance(val, css.Hexcolor):
                p[0] = val
            elif t.type == 'URI':
                p[0] = URI_value(val)
            elif t.type == 'IDENT':
                p[0] = IDENT_value(val)
            elif t.type == 'STRING':
                p[0] = STRING_value(val)
            else:
                p[0] = css.Term(val)
    
    def p_term_quant(self, p):
        '''
        term_quant : NUMBER S
                   | NUMBER
                   | PERCENTAGE S
                   | PERCENTAGE
                   | LENGTH S
                   | LENGTH
                   | EMS S
                   | EMS
                   | EXS S
                   | EXS
                   | ANGLE S
                   | ANGLE
                   | TIME S
                   | TIME
                   | FREQ S
                   | FREQ
        '''
        p[0] = normalize(p[1])
    
    def p_function(self, p):
        '''
        function : FUNCTION S function2
                 | FUNCTION function2
        '''
        name = p[1][:-1] # p[1] has a trailing open-paren
        if len(p) == 4:
            p[0] = css.Function(name, p[3])
        else:
            p[0] = css.Function(name, p[2])
    
    def p_function2(self, p):
        '''
        function2 : expr ')' S
                  | expr ')'
        '''
        p[0] = p[1]
    
    def p_hexcolor(self, p):
        '''
        hexcolor : HASH S
                 | HASH
        '''
        p[0] = css.Hexcolor(p[1])
    
    def p_error(self, p):
        print "Syntax error at '%r'" % p
    

def yacc(**kw):
    kw['module'] = cssparser()
    kw['start'] = 'stylesheet'
    return _yacc.yacc(**kw)
