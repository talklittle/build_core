#!/usr/bin/python

# Copyright 2012, Qualcomm Innovation Center, Inc.
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
    make_status --code <code_file> --base <base_dir> [--deps <dep_file>] [--help]
    Where:
    <code_file>   - Output "C#" code
    <base_dir>    - Root directory for xi:include directives
    <dep_file>    - Ouput makefile dependency file

    """
    global codeOut
    global depOut
    global isFirst
    global fileArgs
    global baseDir

    codeOut = None
    depOut = None
    isFirst = True
    baseDir = ""

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, fileArgs = getopt.getopt(argv, "h", ["help", "code=", "dep=", "base="])
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            if o in ("--code"):
                codeOut = openFile(a, 'w')
            if o in ("--dep"):
                depOut = openFile(a, 'w')
            if o in ("--base"):
                baseDir = a

        if None == codeOut:
            raise Error("Must specify --code")
        
        writeHeaders()

        for arg in fileArgs:
            ret = parseDocument(arg)
            
        writeFooters()

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
        if None != codeOut:
            os.unlink(codeOut.name)
        if None != depOut:
            os.unlink(depOut.name)
        return 1
    
    return 0

def writeHeaders():
    global codeOut
    global depOut
    global fileArgs

    if None != depOut:
        depOut.write("%s %s %s:" % (depOut.name, codeOut.name))
        for arg in fileArgs:
            depOut.write(" \\\n %s" % arg)
    if None != codeOut:
        codeOut.write("""/**                                                                                                   
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

using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.Threading;

namespace AllJoynUnity
{
    public partial class AllJoyn
    {
		/**                                                                                           
         * Enumerated list of values QStatus can return                                               
         */ 
		public class QStatus
        {
            private QStatus(int x)
            {
            
                value = x;
            }

			/** 
			 * Static constructor
			 * @param x status to set for QStatus object
			 */
            public static implicit operator QStatus(int x)
            {
            
                return new QStatus(x);
            }

			/** 
			 * Gets the int value of the QStatus object  
			 *
			 * @param x QStatus object to check status
			 * @return the int value of the QStatus object  
			 */
            public static implicit operator int(QStatus x)
            {
            
                return x.value;
            }

			/** 
			 * Shortcut to determine if a QStatus is an OK status
			 *
			 * @param x QStatus object to check status
			 * @return true if the status == OK
			 */
            public static bool operator true(QStatus x)
            {
            
                return (x == OK);
            }

			/** 
			 * Shortcut to determine if a QStatus is not an OK status
			 *
			 * @param x QStatus object to check status
			 * @return true if the status != OK
			 */
            public static bool operator false(QStatus x)
            {
            
                return (x != OK);
            }

			/** 
			 * Compares the status value of two QStatus objects
			 *
			 * @param x QStatus object to compare with
			 * @param y QStatus object to compare against
			 * @return true if the status values are equal
			 */
            public static bool operator ==(QStatus x, QStatus y)
            {
            
                return x.value == y.value;
            }

			/** 
			 * Compares two QStatus objects
			 *
			 * @param o object to compare against this QStatus
			 * @return true if two QStatus objects are equals
			 */
            public override bool Equals(object o) 
            {
                try
                {
                    return (this == (QStatus)o);
                }
                catch
                {
                    return false;
                }
            }

			/** 
			 * Gets the numeric error code
			 *
			 * @return the numeric error code
			 */
            public override int GetHashCode()
            {
            
                return value;
            }

			/** 
			 * Gets a string representing the QStatus value
			 *
			 * @return a string representing the QStatus value
			 */
            public override string ToString()
            {
            
                return Marshal.PtrToStringAnsi(QCC_StatusText(value));
            }

			/** 
			 * Gets the string representation of the QStatus value
			 *
			 * @param x QStatus object to get value from 
			 * @return the string representation of the QStatus value
			 */
            public static implicit operator string(QStatus x)
            {
            
                return x.value.ToString();
            }

			/** 
			 * Checks if two QStatus objects are not equal
			 *
			 * @param x QStatus object to compare with
			 * @param y QStatus object to compare against
			 * @return true if two QStatus objects are not equal
			 */
            public static bool operator !=(QStatus x, QStatus y)
            {
            
                return x.value != y.value;
            }

			/** 
			 * checks if the QStatus object does not equal OK
			 * 
			 * @param x QStatus object to compare against
			 * @return true if the QStatus object does not equal OK
			 */
            public static bool operator !(QStatus x)
            {
            
                return (x != OK);
            }

            internal int value;
""")

def writeFooters():
    global codeOut
    global depOut

    if None != depOut:
        depOut.write("\n")
    if None != codeOut:
        codeOut.write("""
        }
        #region DLL Imports
        [DllImport(DLL_IMPORT_TARGET)]
        private extern static IntPtr QCC_StatusText(int status);

        #endregion
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
    global codeOut
    global isFirst
    offset = 0

    for node in blockNode.childNodes:
        if node.localName == 'offset':
            offset = int(node.firstChild.data, 0)
        elif node.localName == 'status':
            if None != codeOut:
                codeOut.write("\n            /// %s" % node.getAttribute('comment'))
                codeOut.write("\n            public static readonly QStatus %s = new QStatus(%s);" % (node.getAttribute('name')[3:], node.getAttribute('value')))
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

def UnityStatus(source, output, basedir):
    return main(['--base=%s' % basedir,
                 '--code=%s' % output,
                 '%s' % source])

if __name__ == "__main__":
    sys.exit(main())
