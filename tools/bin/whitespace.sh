#!/bin/bash

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

usage () {
    echo
    echo "Purpose:"
    echo "  Apply uncrustify to source files, recursively, from the present" 
    echo "  working directory.  Enables users to see which source files are not"
    echo "  in compliance with the AllJoyn whitespace policy and fix them."
    echo "  All temporary uncrustify files are removed."
    echo
    echo "Usage:"
    echo "  $1 [check(default)|detail|fix|help] [alljoyn uncrustify cfg]"
    echo
    echo "Commands:"
    echo "  check -  generate a list of files that do not comply (default)"
    echo "  detail - generate a diff of each file that does not comply"
    echo "  fix -    apply (modify) each file that does not comply" 
    echo "  help -   print this message"
    echo
    echo "alljoyn uncrustify cfg:"
    echo "  If the present working directory is the parent directory of the" 
    echo "  alljoyn repositories, or within the alljoyn repositories, then" 
    echo "  the script will attempt to locate the config file, which may be" 
    echo "  found in <install>/build_core/tools/conf/, otherwise, the config" 
    echo "  file may be specified on the command line."
    echo
}

# Locate the uncrustify config file in build_core, assuming that the
# present working directory is the parent directory of the alljoyn
# repositories, or somewhere within the alljoyn repositories.
find_config() {
    tgtdir="build_core"
    curdir="."
    ajcfgrelpath="$tgtdir/tools/conf/ajuncrustify.cfg"
    ajcfgpath=""
    foundit=0
    
    # Easy case.  Check whether build_core is a subdir to pwd.
    ls $curdir | grep $tgtdir > /dev/null
    firstgrepresult=$?
    # echo FIRSTGREP:  $firstgrepresult
    case $firstgrepresult in
        0)
            foundit=1
        ;;

        # Loop through successively higher parent directories. Limit
        # to six levels above pwd.
        1)
            curdir=".."
            for (( c=1; c<=6; c++ ))
            do
                # echo LOOPCURDIR:  $curdir
                ls $curdir | grep $tgtdir > /dev/null
                loopgrepresult=$?
                # echo LOOPGREP:  $loopgrepresult
                case $loopgrepresult in
                    0)
                        foundit=1
                        break
                        ;;
                    1)
                        curdir="$curdir/.."
                        ;;

                    # Something bad has happened, so bail
                    *)  
                        break
                        ;;
                esac    
            done
            ;;
    esac

    # echo FOUNDIT:  $foundit
    # echo FINALCURDIR:  $curdir
    # echo CANDIDATE:  $curdir/$ajcfgrelpath

    # Check if we found the config file location and if the file exists.
    # If true, then assign the location to ajcfgpath.
    # If false, then ajcfgpath remains a zero-length string.
    if [ $foundit==1 ] && [ -f "$curdir/$ajcfgrelpath" ]; then
        # echo WINNER:  $curdir/$ajcfgrelpath
        ajcfgpath=$curdir/$ajcfgrelpath
    fi
}

scriptname=`basename $0`
version_min="0.57"
unc_suffix=".uncrustify"
cmdstrdefault="check"
cmdstr=$cmdstrdefault
cfgspecified=0
unc_cfg=''

# Validate command parameter
if [ $# -ge 1 ]; then
    opt=$( tr '[:upper:]' '[:lower:]' <<<"$1" )
    case $opt in
        check|detail|fix) 
            cmdstr=$opt
            ;;
        h*|?)
            usage $scriptname
            exit 0
            ;;
        *) 
            echo "$1 is an unrecognized command"
            usage $scriptname
            exit 1
    esac
fi

# Check for a config file specified on the cmd line
if [ $# -ge 2 ]; then

    # Verify that specified uncrustify config file exists
    if [ ! -f $2 ]; then
        echo "The specified uncrustify config file, $2, is not a regular file or does not exist"
        usage $scriptname
        exit 1
    fi
    unc_cfg=$2
else
    find_config
    if [ -z $ajcfgpath ]; then
        echo "Unable to locate uncrustify config file.  Please specify on the command line."
        usage $scriptname
        exit 1
    else
        unc_cfg=$ajcfgpath
    fi
fi

echo "Using uncrustify config file:  $unc_cfg"

# Test for installation of uncrustify
uncv=`uncrustify -v`
unc_regex='^uncrustify ([0-9].[0-9]{2})$'
valid_version=0

if [[ "$uncv" =~ $unc_regex ]]; then 

    # Extract the uncrustify version and compare with minimum requirement
    version=${BASH_REMATCH[1]}
    valid_version=`echo "if ($version >= $version_min) print 1 else print 0" | bc -l`

    # If 0 then uncrustify is installed but does not meet version requirement, so we bail
    if [ $valid_version == 0 ]; then 
        echo You are using uncrustify v$version.  You must be using uncrustify v$version_min or later.
        exit 1;
    fi
else

    # If we get to here, then uncrustify does not appear to be installed, so we bail
    echo You must have uncrustify v$version_min or later installed to use this script.
    exit 1;
fi

# Recurse from the current dir and get a list of source files, skipping certain directories
files=`find . -type d -name "stlport" -prune -o \
              -type d -name "build" -prune -o \
              -type d -name ".repo" -prune -o \
              -type d -name ".git" -prune -o \
              \( -name "*.[cChH]" -o -name "*.cc" -o -name "*.cpp" \) \
              -not -name "*~" -not -name ".#*"`

# Loop through the files and apply uncrustify
for srcfile in $files
do
    if [ -f $srcfile ]
    then
        uncfile=$srcfile$unc_suffix
        case $cmdstr in

            # Generate a list of files that do not comply with the whitespace policy
            check)
                uncrustify -q -c $unc_cfg $srcfile
                diff -q $srcfile $uncfile
                rm $uncfile
                ;;

            # Generate a diff of every file that does not comply with the whitespace policy
            detail)
                uncrustify -q -c $unc_cfg $srcfile
                diff -q $srcfile $uncfile > /dev/null
                if [ $? == 1 ]; then
                    echo '****** FILE:'  $srcfile
                    echo '****** BEGIN DIFF ******'
                    echo
                    diff $srcfile $uncfile
                    echo
                    echo '****** END DIFF ******'
                    echo
                    echo
                fi
                rm $uncfile
                ;;

            # Apply whitespace policy to file in-place with NO BACKUP
            fix)
                # The first three cmds simply print a list of what will be modified
                uncrustify -q -c $unc_cfg $srcfile
                diff -q $srcfile $uncfile
                rm $uncfile
                # This cmd will only modify files that differ from the ws policy
                uncrustify -q -c $unc_cfg --no-backup $srcfile
                ;;
        esac
    fi
done
exit 0

