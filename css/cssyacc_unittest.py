#!/usr/bin/env python


import csslex, cssyacc, parse
import unittest, sys


class yacc_test(unittest.TestCase):

    def assertParsedContentEquals(self, input_content, output_contents):
        self.assertEqual(output_contents.strip(), parse.export('fake.css', parse.parse(input_content)).strip())

    def testCharset(self):
        self.assertParsedContentEquals(u'@charset "blah-blee";', u'@charset "blah-blee";')

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
@media print{super{cool:story(bro);}}""")

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
@-webkit-keyframes name{from{some:value;} to{some:other(value);} 0%{width:0;} 100%{width:100px;}}""")

    def testGritStatementList(self):
        self.assertParsedContentEquals(u"""
<if expr="is_macosx">
 @import url(blah.css);
</if>
<if expr="not is_posix">
  <include src="windows.css">
</if>
<if expr="is_chromeos">
   some rule {
     that: is only on "chromeos";
   }
    @-webkit-keyframes name
    {
      from { your: mommas house; }
      to { your: daddys house; }
    }
     @media screen {
       /* screen ftw! */
     }
</if>""", u"""
<if expr="is_macosx">
@import url(blah.css);
</if>
<if expr="not is_posix">
<include src="windows.css">
</if>
<if expr="is_chromeos">
some rule{that:is only on "chromeos";}
@-webkit-keyframes name{from{your:mommas house;} to{your:daddys house;}}
@media screen{}
</if>""")

    def testGritDeclarationList(self):
        self.assertParsedContentEquals(u"""
a {
  b: c;
  d: e;
<if expr="is_oswin">
  f: g;
  h: i();
</if>
  j: 1px solid red;
  k: l m n o p;
}

q {
  r: s;
<if expr="is_macosx">
  t: u;
</if>
  v: w;
}

x {
  y: z;
<if expr="is_osposix">
  aa: bb;
</if>
}

cc {
<if expr="blah blee">
  dd: ee;
</if>
  ff: gg;
}

hh {
<if expr="blee blah">
  hh: ii;
</if>
}""", u"""
a{b:c;d:e;<if expr="is_oswin">f:g;h:i();</if>j:1px solid red;k:l m n o p;}
q{r:s;<if expr="is_macosx">t:u;</if>v:w;}
x{y:z;<if expr="is_osposix">aa:bb;</if>}
cc{<if expr="blah blee">dd:ee;</if>ff:gg;}
hh{<if expr="blee blah">hh:ii;</if>}""")


    def testSelectorAttribute(self):
        self.assertParsedContentEquals(u"""
a[d=e]:not(b) ~ c > e[f|=g][h^=i][j$=k][l*="j"][k~='l'] + m {
  n: o(p);
}""", u"""
a[d=e]:not(b)~c>e[f|=g][h^=i][j$=k][l*="j"][k~='l']+m{n:o(p);}""")


# TODO(dbeam): Figure out how to check for stderr.

      
#    def testSample(self):
#        self.assertParsedContentEquals(u"""
#    """, u"""
#    """)


if __name__ == '__main__':
    unittest.main()
