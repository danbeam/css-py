# -*- coding: utf-8 -*-
'''
A lexical grammar for CSS.
'''

import re
from ply import lex as _lex

__all__ = ('lex','csslexer')

# re helpers

def r_nongroup(rx):
    return ur'(?:' + rx + ur')'

def r_or(*rxs):
    return r_nongroup(ur'|'.join([r_nongroup(x) for x in rxs]))

def r_star(rx):
    return r_nongroup(rx) + ur'*'

def r_plus(rx):
    return r_nongroup(rx) + ur'+'

def r_opt(rx):
    return r_nongroup(rx) + ur'?'


# lexer


softsp         = r_opt(r_or(ur'\r\n', ur'[ \t\r\n\f]'))

s              = r_plus(ur'[ \t\r\n\f]')
w              = r_opt(s)
nl             = ur'\n|\r\n|\r|\f'

h              = ur'[0-9a-fA-F]'
nonascii       = ur'[^\0-\177]'
unicode        = ur'\\' + h + ur'{1,6}' + softsp
escape         = r_or(unicode, ur'\\[^\r\n\f0-9a-fA-F]')
nmstart        = r_or(ur'[_a-zA-Z]', nonascii, escape)
nmchar         = r_or(ur'[_a-zA-Z0-9-]', nonascii, escape)
string1        = ur'"%s"' % r_star(r_or(ur'[^\n\r\f\\"]',
                                       ur'\\' + nl,
                                       escape))
string2        = r"'%s'" % r_star(r_or(ur"[^\n\r\f\\']",
                                       ur'\\' + nl,
                                       escape))
invalid1       = ur'"%s' % r_star(r_or(ur'[^\n\r\f\\"]',
                                      ur'\\'+nl,
                                      escape))
invalid2       = r"'%s" % r_star(r_or(ur"[^\n\r\f\\']",
                                      ur'\\'+nl,
                                      escape))

comment        = ur'\/\*[^*]*\*+(?:[^/][^*]*\*+)*\/'
comment        = ur'\/\*' + r_star(ur'[^*]') + r_plus(ur'\*') + \
                 r_star(ur'[^/]' + r_star(ur'[^*]') + r_plus(ur'\*')) + \
                 ur'\/'

ident          = r_opt(ur'-') + nmstart + r_star(nmchar)
name           = r_plus(nmchar)
num            = r_or(r_star(ur'[0-9]') + ur'\.' + r_plus(ur'[0-9]'),
                      r_plus(ur'[0-9]'))
string         = r_or(string1, string2)
invalid        = r_or(invalid1, invalid2)
url            = r_star(r_or(ur'[!#$%&*-~]', nonascii, escape))

def letter(c):
    return r_or(c.lower(),
                ur'\\0{0,4}' +
                r_or(hex(ord(c.upper()))[2:], hex(ord(c.lower()))[2:]) +
                softsp)

def normalize(x):
    '''Normalizes escaped characters to their literal value.'''
    p = ur'\\0{0,4}([0-9]{2})'
    r = lambda m: chr(int(m.groups()[0],16))
    return re.sub(p,r,x).lower()

A              = letter(u'A')
B              = letter(u'B')
C              = letter(u'C')
D              = letter(u'D')
E              = letter(u'E')
F              = letter(u'F')
G              = letter(u'G')
H              = letter(u'H')
I              = letter(u'I')
J              = letter(u'J')
K              = letter(u'K')
L              = letter(u'L')
M              = letter(u'M')
N              = letter(u'N')
O              = letter(u'O')
P              = letter(u'P')
Q              = letter(u'Q')
R              = letter(u'R')
S              = letter(u'S')
T              = letter(u'T')
U              = letter(u'U')
U              = letter(u'V')
W              = letter(u'W')
X              = letter(u'X')
Y              = letter(u'Y')
Z              = letter(u'Z')


# %%


class csslexer(object):
    literals = list(ur'*-:;.=/)}[]')

    tokens = (
        'ANGLE',
        'CDC',
        'CDO',
        'CHARSET_SYM',
        'COMMA',
        'DASHMATCH',
        'DIMENSION',
        'EMS',
        'EXS',
        'FREQ',
        'FUNCTION',
        'GREATER',
        'GRIT_EXPR',
        'GRIT_IF',
        'GRIT_IF_END',
        'GRIT_INCLUDE',
        'HASH',
        'IDENT',
        'IMPORTANT_SYM',
        'IMPORT_SYM',
        'INCLUDES',
        'INVALID',
        'KEYFRAMES_SYM',
        'LBRACE',
        'LENGTH',
        'MEDIA_SYM',
        'NOT',
        'NUMBER',
        'PAGE_SYM',
        'PERCENTAGE',
        'PLUS',
        'PREFIXMATCH',
        'S',
        'STRING',
        'SUBSTRINGMATCH',
        'SUFFIXMATCH',
        'TILDE',
        'TIME',
        'URI',
        )

    # several of the following are defined as functions rather
    # than simple rules so that tokenizing precedence works properly,
    # i.e. lengths, etc. are not parsed as dimensions

    t_S              = s

    # comments are ignored, but line breaks are counted
    @_lex.TOKEN(comment)
    def t_COMMENT(self, t):
        t.lexer.lineno += len(re.findall(nl,t.value))
        return None

    t_CDO            = ur'\<\!\-\-'
    t_CDC            = ur'\-\-\>'

    t_LBRACE         = w + ur'\{'
    t_PLUS           = w + ur'\+'
    t_GREATER        = w + ur'\>'
    t_COMMA          = w + ur'\,'
    t_TILDE          = w + ur'\~'

    t_INCLUDES       = t_TILDE + ur'\='
    t_DASHMATCH      = ur'\|\='
    t_PREFIXMATCH    = ur'\^\='
    t_SUFFIXMATCH    = ur'\$\='
    t_SUBSTRINGMATCH = ur'\*\='
    t_NOT            = ur'\:' + N + O + T + '\('

    @_lex.TOKEN(string)
    def t_STRING(self, t):
        t.lexer.lineno += len(re.findall(nl,t.value))
        return t

    @_lex.TOKEN(invalid)
    def t_INVALID(self, t):
        t.lexer.lineno += len(re.findall(nl,t.value))
        return t

    t_IDENT          = ident

    t_HASH           = ur'\#' + name

    t_IMPORT_SYM     = ur'@' + I + M + P + O + R + T
    t_PAGE_SYM       = ur'@' + P + A + G + E
    t_MEDIA_SYM      = ur'@' + M + E + D + I + A
    t_KEYFRAMES_SYM  = ur'@\-' + W + E + B + K + I + T + ur'\-' + K + E + Y + F + R + A + M + E + S

    # Per the CSS 2.1 errata, the charset rule must be in lowercase
    # and must have a trailing space.
    t_CHARSET_SYM    = ur'@charset\ '

    t_IMPORTANT_SYM  = ur'\!' + \
        r_star(r_or(w,comment)) + \
        I + M + P + O + R + T + A + N + T

    t_GRIT_EXPR      = E + X + P + R
    t_GRIT_IF        = ur'\<' + I + F
    t_GRIT_IF_END    = ur'\<' + r_star(s) + '\/' + r_star(s) + I + F + r_star(s) + t_GREATER
    t_GRIT_INCLUDE   = ur'\<' + I + N + C + L + U + D + E

    @_lex.TOKEN(num + E + M)
    def t_EMS(self, t):
        return t

    @_lex.TOKEN(num + E + X)
    def t_EXS(self, t):
        return t

    @_lex.TOKEN(num + r_or(P + X, r_or(C, M) + M, I + N, P + r_or(T, C)))
    def t_LENGTH(self, t):
        return t

    @_lex.TOKEN(num + r_or(D + E + G, r_opt(G) + R + A + D))
    def t_ANGLE(self, t):
        return t

    @_lex.TOKEN(num + r_opt(M) + S)
    def t_TIME(self, t):
        return t

    @_lex.TOKEN(num + r_opt(K) + H + Z)
    def t_FREQ(self, t):
        return t

    @_lex.TOKEN(num + ident)
    def t_DIMENSION(self, t):
        return t

    @_lex.TOKEN(num + ur'%')
    def t_PERCENTAGE(self, t):
        return t

    t_NUMBER       = num

    @_lex.TOKEN(U + R + L + ur'\(' + w + r_or(string, url) + w + ur'\)')
    def t_URI(self, t):
        return t

    @_lex.TOKEN(ident + ur'\(')
    def t_FUNCTION(self, t):
        return t

    def t_error(self, t):
        print "Illegal token '%s'" % t.value[0]
        t.lexer.skip(1)



def lex(**kw):
    if 'object' in kw: del kw['object']
    kw['module'] = csslexer()
    if 'reflags' not in kw:
        kw['reflags'] = 0
    kw['reflags'] |= re.UNICODE | re.IGNORECASE
    return _lex.lex(**kw)

if '__main__' == __name__:
    _lex.runmain(lexer=lex())
