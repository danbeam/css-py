# -*- coding: utf-8 -*-
'''
Classes representing CSS syntactic concepts.
'''

import re
import itertools
import serialize

__all__ = ('Hexcolor', 'Function', 'Uri', 'String', 'Ident',
           'Term', 'Declaration', 'Ruleset', 'Charset', 'Page',
           'Media', 'Import', 'Stylesheet')

class SyntaxObject(object):
    '''
    An abstract type of syntactic construct.
    '''
    def __str__(self):
        return self.datum(str)

    def __unicode__(self):
        return self.datum(unicode)

re_hexcolor = re.compile(r'#[0-9a-fA-F]{3,6}$')

class Hexcolor(SyntaxObject):
    '''
    An RGB color in hex notation.
    
    The value must begin with a # character and contain 3 or 6 hex digits.
    '''
    def __init__(self, value):
        if not re.match(re_hexcolor,value):            
            raise ValueError, '''Hexcolor values must start with # and contain 3 or 6 hex digits.'''
        
        self.value = value[1:]

    def __repr__(self):
        return 'Hexcolor(%r)' % ('#'+self.value,)

    def datum(self, serializer):
        return serialize.serialize_Hexcolor(self, serializer)

class Function(object):
    '''
    A term in functional notation, e.g. colors specified with rgb().
    
    Note: although URIs are specified with the functional notation url(),
    they are a distinct type of data.
    '''
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    def __repr__(self):
        return 'Function(%r, %r)' % (self.name, self.parameters)

    def datum(self, serializer):
        return serialize.serialize_Function(self, serializer)
    

class Uri(SyntaxObject):
    '''
    An URI.
    '''
    def __init__(self, url):
        if isinstance(url, String):
            url = url.value
        self.url = url

    def __repr__(self):
        return 'Uri(%r)' % (self.url,)

    def datum(self, serializer):
        return serialize.serialize_Uri(self, serializer)

class String(SyntaxObject):
    '''
    A string of characters delimited by quotation marks.
    '''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'String(%r)' % (self.value,)

    def datum(self, serializer):
        return serialize.serialize_String(self, serializer)

class Ident(SyntaxObject):
    '''
    An identifier.
    '''
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Ident(%r)' % (self.name,)

    def datum(self, serializer):
        return serialize.serialize_Ident(self, serializer)

class Term(SyntaxObject):
    '''
    An expression term, other than a Ident, Function or Hexcolor.
    
    Quantitative terms, such as EMS may have a - or + sign as
    a unary operator.
    '''
    def __init__(self, value, unary_operator=None):
        if unary_operator and -1 == '-+'.find(unary_operator):
            raise ValueError, '''unary operator, if given, must be - or +'''
        self.value = value
        self.unary_operator = unary_operator

    def __repr__(self):
        r = 'Term(' + repr(self.value)
        if self.unary_operator:
            r += ', unary_operator=' + repr(self.unary_operator)
        r += ')'
        return r

    def datum(self, serializer):
        return serialize.serialize_Term(self, serializer)
    

class Declaration(SyntaxObject):
    '''
    A property-value declaration with an optional important flag.
    '''
    def __init__(self, property, value, important=False):
        self.property = property
        self.value = value
        self.important = important

    def __repr__(self):
        r = 'Declaration(' + repr(self.property)
        r += ', ' + repr(self.value)
        if self.important:
            r += ', important=True'
        r += ')'
        return r

    def datum(self, serializer):
        return serialize.serialize_Declaration(self, serializer)
    

class Ruleset(SyntaxObject):
    '''
    A list of declarations for a given list of selectors.

    When iterating, yields each of its declarations in order of
    their appearance.
    '''
    def __init__(self, selectors, declarations=None):
        self.selectors = selectors
        self.declarations = declarations or list()

    def __repr__(self):
        r = 'Ruleset(' + repr(self.selectors)
        if self.declarations:
            r += ', declarations=' + repr(self.declarations)
        r += ')'
        return r
    
    def __iter__(self):
        return iter(self.declarations)

    def __len__(self):
        return len(self.declarations)

    def __getitem__(self, key):
        return self.declarations[key]

    def datum(self, serializer):
        return serialize.serialize_Ruleset(self, serializer)

class Charset(SyntaxObject):
    '''
    A @charset rule indicating the character encoding of a stylesheet.
    '''
    def __init__(self, encoding):
        self.encoding = encoding

    def __repr__(self):
        return 'Charset(%r)' % (self.encoding,)

    def datum(self, serializer):
        return serialize.serialize_charset(self, serializer)
    

class Page(SyntaxObject):
    '''
    A @page rule statement containing a list of declarations.
    
    The rule may have a pseudo-page specifer like :left or :right.

    When iterating, yields each of its declarations in order of
    their appearance.
    '''
    def __init__(self, declarations=None, pseudo_page=None):
        self.declarations = declarations or list()
        self.pseudo_page = pseudo_page

    def __repr__(self):
        r = 'Page(' + repr(self.declarations)
        if self.pseudo_page:
            r += ', pseudo_page=' + repr(self.pseudo_page)
        r += ')'
        return r
    
    def __iter__(self):
        return iter(self.declarations)

    def __len__(self):
        return len(self.declarations)

    def __getitem__(self, key):
        return self.declarations[key]

    def datum(self, serializer):
        return serialize.serialize_Page(self, serializer)
    

class Media(SyntaxObject):
    '''
    An @media rule statement containing a list of rulesets.

    When iterating, yields each of its rulesets in order of
    their appearance.
    '''
    def __init__(self, media_types, rulesets=None):
        self.media_types = media_types
        self.rulesets = rulesets or list()

    def __repr__(self):
        r = 'Media(' + repr(self.media_types)
        if self.rulesets:
            r += ', rulesets=' + repr(self.rulesets)
        r += ')'
        return r 
    
    def __iter__(self):
        return iter(self.rulesets)

    def __len__(self):
        return len(self.rulesets)

    def __getitem__(self, key):
        return self.rulesets[key]

    def datum(self, serializer):
        return serialize.serialize_Media(self, serializer)

class Import(SyntaxObject):
    '''
    An @import rule statement.
    
    May have an optional list of media type specifiers.
    '''
    def __init__(self, source, media_types=None):
        if not isinstance(source, Uri):
            source = Uri(source)
        self.source = source
        self.media_types = media_types or list()

    def __repr__(self):
        r = 'Import(' + repr(self.source)
        if self.media_types:
            r += ', media_types=' + repr(self.media_types)
        r += ')'
        return r

    def datum(self, serializer):
        return serialize.serialize_Import(self, serializer)

class Stylesheet(SyntaxObject):
    '''
    A CSS stylesheet containing a list of statements.
    
    May have an optional list of import rules and an optional 
    character set specification.

    When iterating, yields each of its rules, including @import 
    and @charset rules, in order of their appearance.
    '''
    def __init__(self, statements, imports=None, charset=None):
        self.statements = statements
        self.imports = imports or list()
        self.charset = charset
    
    def __repr__(self):
        r = 'Stylesheet(' + repr(self.statements)
        if self.imports:
            r += ', imports=' + repr(self.imports)
        if self.charset:
            r += ', charset=' + repr(self.charset)
        r += ')'
        return r
    
    def __iter__(self):
        its = list()
        if self.charset:
            its.append([self.charset])
        if self.imports:
            its.append(self.imports)
        its.append(self.statements)
        return itertools.chain(*its)

    def __len__(self):
        n = len(self.statements) + len(self.imports)
        if self.charset:
            n += 1
        return n

    def __getitem__(self, key):
        return list(self)[key]

    def datum(self, serializer):
        return serialize.serialize_Stylesheet(self, serializer)        



    

