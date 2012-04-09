#!/usr/bin/python

# Copyright 2011, Qualcomm Innovation Center, Inc.
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# 

import sys
import os
import getopt
from xml.dom import minidom

if sys.version_info[:3] < (2,4,0):
    from sets import Set as set

includeSet = set()

def openFile(name, type):
    try:
        return open(name, type)
    except IOError, e:
        errno, errStr = e
        print "I/O Operation on %s failed" % name
        print "I/O Error(%d): %s" % (errno, errStr)
        raise e


def main(argv=None):
    """
    make_status --code <code_file> --base <base_dir> --widl <widl_in_file> [--help]
    Where:
    <code_file>    - Output "WIDL" code
    <base_dir>     - Root directory for xi:include directives
    <widl_in_file> - Input "WIDL" code

    """
    global codeOut
    global isFirst
    global fileArgs
    global baseDir
    global widlIn

    codeOut = None
    isFirst = True
    baseDir = ""
    widlIn = None

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, fileArgs = getopt.getopt(argv, "h", ["help", "code=", "widl=", "base="])
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            if o in ("--code"):
                codeOut = openFile(a, 'w')
            if o in ("--widl"):
                widlIn = openFile(a, 'r')
            if o in ("--base"):
                baseDir = a

        if None == codeOut:
            raise Error("Must specify --code")
        if None == widlIn:
            raise Error("Must specify --widl")

        lines = widlIn.readlines()

        codeOut.write('/* This file is auto-generated.  Do not modify. */\n')
        for l in lines:
            if l.find('##STATUS##') >= 0:
                for arg in fileArgs:
                    ret = parseDocument(arg)
            else:
                codeOut.write(l)

        if None != codeOut:
            codeOut.close()
        if None != widlIn:
            widlIn.close()
    except getopt.error, msg:
        print msg
        print "for help use --help"
        return 1
    except Exception, e:
        print "ERROR: %s" % e
        if None != codeOut:
            os.unlink(codeOut.name)
        return 1
    
    return 0


def parseDocument(fileName):
    dom = minidom.parse(fileName)
    for child in dom.childNodes:
        if child.localName == 'status_block':
            parseStatusBlock(child)
        elif child.localName == 'include' and child.namespaceURI == 'http://www.w3.org/2001/XInclude':
            parseInclude(child)
    dom.unlink()

def parseStatusBlock(blockNode):
    global codeOut
    offset = 0

    for node in blockNode.childNodes:
        if node.localName == 'offset':
            offset = int(node.firstChild.data, 0)
        elif node.localName == 'status':
            if None != codeOut:
                codeOut.write("    /** %s */\n" % node.getAttribute('comment'))
                codeOut.write("    const unsigned short %s = %s;\n" % (node.getAttribute('name')[3:], node.getAttribute('value')))
            offset += 1
        elif node.localName == 'include' and node.namespaceURI == 'http://www.w3.org/2001/XInclude':
            parseInclude(node)

def parseInclude(includeNode):
    global baseDir
    global includeSet

    href = os.path.join(baseDir, includeNode.attributes['href'].nodeValue)
    if href not in includeSet:
        includeSet.add(href)
        parseDocument(href)

def Widl(widlIn, statusXml, widlOut):
    return main(['--base=%s' % os.path.abspath('.'),
                 '--widl=%s' % widlIn,
                 '--code=%s' % widlOut,
                 '%s' % statusXml])

if __name__ == "__main__":
    sys.exit(main())
