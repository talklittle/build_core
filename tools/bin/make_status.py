#!/usr/bin/python

# Copyright 2010 - 2011, Qualcomm Innovation Center, Inc.
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
    make_status --header <header_file> --code <code_file> --prefix <prefix> --base <base_dir> [--deps <dep_file>] [--help]
    Where:
      <header_file> - Output "C" header file
      <code_file>   - Output "C" code
      <prefix>      - Prefix which is unique across all projects (see Makefile XXX_DIR)
      <base_dir>    - Root directory for xi:include directives
      <dep_file>    - Ouput makefile dependency file

    """
    global headerOut
    global codeOut
    global depOut
    global isFirst
    global fileArgs
    global baseDir
    global prefix

    headerOut = None
    codeOut = None
    depOut = None
    isFirst = True
    baseDir = ""
    prefix = ""

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, fileArgs = getopt.getopt(argv, "h", ["help", "header=", "code=", "dep=", "base=", "prefix="])
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            if o in ("--header"):
                headerOut = openFile(a, 'w')
            if o in ("--code"):
                codeOut = openFile(a, 'w')
            if o in ("--dep"):
                depOut = openFile(a, 'w')
            if o in ("--base"):
                baseDir = a
            if o in ("--prefix"):
                prefix = a

        if None == headerOut or None == codeOut:
            raise Error("Must specify both --header and --code")

        writeHeaders()

        for arg in fileArgs:
            ret = parseDocument(arg)
            
        writeFooters()

        if None != headerOut:
            headerOut.close()
        if None != codeOut:
            codeOut.close()
        if None != depOut:
            depOut.close()
    except getopt.error, msg:
        print msg
        print "for help use --help"
        return 1
    except Exception, e:
        print "ERROR: %s" % e
        if None != headerOut:
            os.unlink(headerOut.name)
        if None != codeOut:
            os.unlink(codeOut.name)
        if None != depOut:
            os.unlink(depOut.name)
        return 1
    
    return 0

def writeHeaders():
    global headerOut
    global codeOut
    global depOut
    global fileArgs

    if None != depOut:
        depOut.write("%s %s %s:" % (depOut.name, codeOut.name, headerOut.name))
        for arg in fileArgs:
            depOut.write(" \\\n %s" % arg)
    if None != headerOut:
        headerOut.write("""
/**
 * @file
 * This file contains an enumerated list values that QStatus can return
 *
 * Note: This file is generated during the make process.
 *
 * Copyright 2009-2011, Qualcomm Innovation Center, Inc.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.   
 */ 
#ifndef _STATUS_H
#define _STATUS_H

#ifndef ALLJOYN_DLLExport /* Used for extern C functions. Add __declspec(dllexport) when using MSVC */
#  if defined(_MSC_VER) /* MSVC compiler*/
#    define ALLJOYN_DLLExport __declspec(dllexport)
#  else /* compiler other than MSVC */
#    define ALLJOYN_DLLExport
#  endif /* Compiler type */
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Enumerated list of values QStatus can return
 */
typedef enum {""")

    if None != codeOut:
        codeOut.write("""

#include "Status.h"

#define CASE(_status) case _status: return #_status 
    
""")
        codeOut.write("const char* QCC_%sStatusText(QStatus status)" % prefix)
        codeOut.write("""
{
    switch (status) {
""")


def writeFooters():
    global headerOut
    global codeOut
    global depOut

    if None != depOut:
        depOut.write("\n")
    if None != headerOut:
        headerOut.write("""
} QStatus;

/**
 * Convert a status code to a C string.
 *
 * @c %QCC_StatusText(ER_OK) returns the C string @c "ER_OK"
 *
 * @param status    Status code to be converted.
 *
 * @return  C string representation of the status code.
 */
""")
        headerOut.write("extern ALLJOYN_DLLExport const char* QCC_%sStatusText(QStatus status);" % prefix)
        headerOut.write("""

#ifdef __cplusplus
}   /* extern "C" */
#endif

#endif
""")
    if None != codeOut:
        codeOut.write("""    default:
        return "<unknown>";
    }
}
""")

    
def parseDocument(fileName):
    dom = minidom.parse(fileName)
    for child in dom.childNodes:
        if child.localName == 'status_block':
            parseStatusBlock(child)
        elif child.localName == 'include' and child.namespaceURI == 'http://www.w3.org/2001/XInclude':
            parseInclude(child)
    dom.unlink()

def parseStatusBlock(blockNode):
    global headerOut
    global codeOut
    global isFirst
    offset = 0

    for node in blockNode.childNodes:
        if node.localName == 'offset':
            offset = int(node.firstChild.data, 0)
        elif node.localName == 'status':
            if isFirst:
                if None != headerOut:
                    headerOut.write("\n    %s = %s /**< %s */" % (node.getAttribute('name'), node.getAttribute('value'), node.getAttribute('comment')))
                isFirst = False
            else:
                if None != headerOut:
                    headerOut.write(",\n    %s = %s /**< %s */" % (node.getAttribute('name'), node.getAttribute('value'), node.getAttribute('comment')))
            if None != codeOut:
                codeOut.write("        CASE(%s);\n" % (node.getAttribute('name')))
            offset += 1
        elif node.localName == 'include' and node.namespaceURI == 'http://www.w3.org/2001/XInclude':
            parseInclude(node)


def parseInclude(includeNode):
    global baseDir
    global includeSet

    href = os.path.join(baseDir, includeNode.attributes['href'].nodeValue)
    if href not in includeSet:
        includeSet.add(href)
        if None != depOut:
            depOut.write(" \\\n %s" % href)
        parseDocument(href)


if __name__ == "__main__":
    sys.exit(main())

#end
