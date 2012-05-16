#!/usr/bin/env python


import csslex, cssyacc
import parse
import unittest


class yacc_test(unittest.TestCase):

    def assertParsedContentEquals(self, input, output):
        self.assertEqual(output.strip(), parse.export('fake.css', parse.parse(input)).strip())

    def testImportStatements(self):
        self.assertParsedContentEquals(u"""
@import 'file.css';
 @import "file.css";
  @import url(http://hostname/file.css);
   <include src='blah.css'>
    <include src="blah.css">""", u"""
@import url(file.css);
@import url(file.css);
@import url(http://hostname/file.css);
<include src='blah.css'>
<include src="blah.css">""")

    def testMediaStatement(self):
          self.assertParsedContentEquals(u"""
/* TODO(dbeam): Media queries? */
@media print {
  super {
    cool: story(bro);
  }
}""", u"""
@media print{super{cool:story(bro)}}""")

    def testKeyframesRule(self):
        self.assertParsedContentEquals(u"""
@-webkit-keyframes name{
  from { some: value; }
  to {
    some: other(value);
  }
  0% {
    width: 0;
  }
  100% { width: 100px; }
}""", u"""
@-webkit-keyframes name{from{some:value} to{some:other(value)} 0%{width:0} 100%{width:100px}}""")


#    def testSample(self):
#        self.assertParsedContentEquals(u"""
#    """, u"""
#    """)


if __name__ == '__main__':
  unittest.main()
