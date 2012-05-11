#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
from codecs import EncodedFile
import css, csslex, cssyacc
from uri import uri
from os import path

__all__ = ('parse','export')

def parse(data):
    parser = cssyacc.yacc()
    parser.lexer = csslex.lex()
    return parser.parse(data) #, debug=True)

def export(base, stylesheet, recursive=False):
    def recur(rule):
        export(base, parse(url_or_file(rule.source).read()), recursive)

    for rule in stylesheet:
        if recursive and isinstance(rule, css.Import):
            recur(rule)
        else:
            print rule.datum(unicode)

def url_or_file(f):
    if isinstance(f, css.Uri):
        f = f.url
    return open(f) if path.exists(f) else urlopen(f)


def main(files_or_uris, options):
    for i, f in enumerate(files_or_uris):
        infile = url_or_file(f)
        print '%s/* %s: %s */' % (u'' if i == 0 else u'\n', u'file' if isinstance(infile, file) else u'url', f)
        export(f, parse(infile.read()), recursive=options.recursive)
    

if '__main__' == __name__:
    from optparse import OptionParser
    opts = OptionParser("usage: %prog [options] <file_or_urls>")
    opts.add_option('-r', '--recursive', dest='recursive', action='store_true', default=False)
    options, args = opts.parse_args()

    if len(args) == 0:
        opts.error("no file[s] or url[s] given")
        
    main(args, options)
