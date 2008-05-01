#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
from codecs import EncodedFile
import css, csslex, cssyacc
from serialize import serialize
from uri import uri


def parse(data):
    parser = cssyacc.yacc()
    parser.lexer = csslex.lex()
    return parser.parse(data, debug=True)

def export(stylesheet):
    if stylesheet.charset:
        print serialize(stylesheet.charset, unicode)

    for i in stylesheet.imports:
        url = i.source
        if isinstance(url, css.Uri):
            url = url.url
            importuri = uri.resolve(fileuri, url)
            importfile = urlopen(importuri)
            export(parse(importfile.read()))

    for s in stylesheet.statements:
        print serialize(s, unicode)

if '__main__' == __name__:
    from optparse import OptionParser
    opts = OptionParser("usage: %prog [options] filename")

    options, args = opts.parse_args()

    if 1 != len(args):
        opts.error("no filename given")

    fileuri = args[0]

    inputfile = urlopen(fileuri)

    stylesheet = parse(inputfile.read())
    export(stylesheet)
