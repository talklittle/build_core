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

import sys, os, fnmatch, argparse, re, filecmp, difflib, textwrap
from subprocess import Popen, STDOUT, PIPE

def main( ):
    dir_ignore = ["stlport", "build", ".git", ".repo"]
    file_ignore_patterns = ['\.#.*', 'alljoyn_java\.h', 'Status\.h']
    file_patterns = ['*.c', '*.h', '*.cpp', '*.cc']
    valid_commands = ["check", "detail", "fix"]
    uncrustify_config = None
    version_min = 0.57
    unc_suffix = ".uncrustify"
    
    parser = get_parser()
    ns = parser.parse_args()
    if ns.wscmd not in valid_commands:
        print "\'" + ns.wscmd + "\'" + " is not a valid command"
        parser.print_help()
        sys.exit(1)
    
    '''If config specified in CL then use that, otherwise search for it'''    
    if ns.wscfg:
        uncrustify_config = ns.wscfg.name
    else:
        uncrustify_config = find_config()
        
    if not uncrustify_config:
        print "Unable to find a config file"
        parser.print_help()
        sys.exit(1)
    
    version = uncrustify_version()    
    if version < version_min:
        print ("You are using uncrustify v" + str(version) + 
            ". You must be using uncrustify v" + str(version_min) + 
            " or later.")
        sys.exit(1)
    
    '''Get a list of source files and apply uncrustify to them'''   
    for srcfile in locate(file_patterns, file_ignore_patterns, dir_ignore):
        uncfile = srcfile + unc_suffix
        
        '''Run uncrustify and generate uncrustify output file'''
        Popen(["uncrustify", "-q", "-c", 
            uncrustify_config, srcfile], stdout=PIPE).communicate()[0]
        
        '''check command'''
        if ns.wscmd == valid_commands[0]: 
            
            '''If the src file and the uncrustify file are different
            then print the filename'''             
            if not filecmp.cmp(srcfile, uncfile, False):
                print srcfile
        
        '''detail command'''    
        if ns.wscmd == valid_commands[1]:
            
            '''If the src file and the uncrustify file are different
            then diff the files'''
            if not filecmp.cmp(srcfile, uncfile, False):
                print ''
                print '******** FILE: ' + srcfile
                print ''
                print '******** BEGIN DIFF ********'
                
                fromlines = open(srcfile, 'U').readlines()
                tolines = open(uncfile, 'U').readlines()
                diff = difflib.unified_diff(fromlines, tolines, n=0)
                sys.stdout.writelines(diff)

                print ''
                print '********* END DIFF *********'
                print ''
            
        '''fix command'''
        if ns.wscmd == valid_commands[2]:
            
            '''If the src file and the uncrustify file are different
            then print the filename so that the user can see what will 
            be fixed'''
            if not filecmp.cmp(srcfile, uncfile, False):
                print srcfile
            
            '''run uncrustify again and overwrite the non-compliant file with
            the uncrustify output'''
            Popen(["uncrustify", "-q", "-c", 
                    uncrustify_config, "--no-backup", 
                    srcfile], stdout=PIPE).communicate()[0]
        
        '''remove the uncrustify output file'''            
        if os.path.exists(uncfile):
            os.remove(uncfile)

'''Return the uncrustify version number'''
def uncrustify_version( ):
    version = None
    
    try:
        '''run the uncrustify version command'''
        output = Popen(["uncrustify", "-v"], stdout=PIPE).communicate()[0]
    
    except OSError:
        '''OSError probably indicates that uncrustify is not installed,
         so bail after printing helpful message'''
        print ("It appears that \'uncrustify\' is not installed or is not " + 
            "on your PATH. Please check your system and try again.")
        sys.exit(1)
    
    else:
        '''if no error, then extract version from output string and convert 
        to floating point'''
        p = re.compile('^uncrustify (\d.\d{2})')
        m = re.search(p, output)
        version = float(m.group(1))
    
    return version

'''Command line argument parser'''    
def get_parser( ):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Apply uncrustify to C++ source files (.c, .h, .cc, .cpp), 
        recursively, from the present working directory.  Skips 
        'stlport', 'build', '.git', and '.repo' directories.
        
        Note:  present working directory is presumed to be within,
        or the parent of, one of the AllJoyn archives.
        
        Script will automatically locate the uncrustify config file
        in build_core, or alternatively, the user may specify one.  
        
        Enables users to see which source files are not in compliance 
        with the AllJoyn whitespace policy and fix them as follows:  
        
            check     - prints list of non-compliant files (default)
            detail    - prints diff of non-compliant files 
            fix       - modifies (fixes) non-compliant files 
            
        Note that all files generated by uncrustify are removed.'''),
        epilog=textwrap.dedent('''\
        Examples:
        
        Get a list of non-compliant files using the alljoyn uncrustify config:
            >python %(prog)s  --OR--
            >python %(prog)s check
        
        Get a list of non-compliant files using your own uncrustify config:
            >python %(prog)s check myconfig.cfg
        
        Get a diff of non-compliant files using the alljoyn uncrustify config:
            >python %(prog)s detail
        
        Fix non-compliant files using the alljoyn uncrustify config:
            >python %(prog)s fix
        '''))
        
    parser.add_argument(    'wscmd', 
                            nargs='?', 
                            default='check', 
                            metavar='command',
                            help='options:  check(default) | detail | fix')
                            
    parser.add_argument(    'wscfg',
                            type=file, 
                            nargs='?', 
                            metavar='uncrustify config',
                            help='specify an alternative uncrustify config (default=none)')
                            
    return parser

'''Search for the uncrustify config file'''            
def find_config( ):
    tgtdir = "build_core"
    cfgname = "ajuncrustify.cfg"
    ajcfgrelpath = os.path.join(tgtdir, "tools", "conf", cfgname)
    ajcfgpath = None
    foundit = 0
    DIRDEPTHMAX = 6
    curdir = None
    
    '''Limit directory search to depth DIRDEPTHMAX'''
    for i in range(DIRDEPTHMAX):
        curdir = os.getcwd()
        if tgtdir in os.listdir(curdir):
            foundit = 1
            break
        else:
            os.chdir("..")
    
    if foundit == 1 and os.path.exists(os.path.join(curdir, ajcfgrelpath)):
        ajcfgpath = os.path.join(curdir, ajcfgrelpath)        
                
    return ajcfgpath        

'''Recurse through directories and locate files that match a given pattern'''
def locate(file_patterns, file_ignore_patterns, dir_ignore_patterns, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        '''Remove unwanted dirs'''
        for dip in dir_ignore_patterns:
            for dyr in dirs:
                if dyr == dip:
                    dirs.remove(dyr)
        '''Remove unwanted files'''            
        for filename in files:
            for fip in file_ignore_patterns:
                if re.search(fip, filename):
                    files.remove(filename)
        '''Filter the remainder using our wanted file pattern list'''    
        for pattern in file_patterns:
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)
 
if __name__ == "__main__":
    sys.exit(main())

#end               
