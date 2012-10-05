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

# A simple C# builder with no extra bells or whistles

import os.path
import SCons.Builder
import SCons.Node.FS
import SCons.Util

cs_action = '$CSC "/target:exe" $_CSC_FLAGS "/out:${TARGET.abspath}" ${SOURCES}'
#cs_lib_action = "csc.exe /target:library /out:${TARGET} ${SOURCE.dir}\*.cs $_CSC_FLAGS"
cs_lib_action = '$CSC "/target:library" $_CSC_LIB_PATHS $_CSC_REFERENCES "/out:${TARGET.abspath}" ${SOURCES}'
cs_suffix = '.exe'
cs_lib_suffix = '.dll'

# This SCons Builder does not properly calculate the dependencies for the .NET 
# Framework Assemblies specified when using the CSC_REFERENCES do make sure a  
# Framework Assembly exist a person should use env.Depends for each Assembly listed
# in the CSC_REFERENCES 

def generate(env):
    cs_builder = SCons.Builder.Builder(action = '$CSC_ACTION', src_suffix = '.cs', suffix = cs_suffix)
    cs_lib_builder = SCons.Builder.Builder(action = '$CSC_LIB_ACTION', src_suffix = '.cs', suffix = cs_lib_suffix)
    
    env['BUILDERS']['CSharp'] = cs_builder
    env['BUILDERS']['CSharpLib'] = cs_lib_builder
    
    #define the C# compiler
    env['CSC'] = 'csc.exe'
    # A list of compiler flags like debug, warn, noconfig, or nologo 
    env['CSC_FLAGS'] = ''
    env['_CSC_FLAGS'] = "${_stripixes('\"/', CSC_FLAGS, '\"', '\"/', '\"', __env__)}" 
    # A list of compiler flags when building a library file
    env['CSC_LIB_FLAGS'] = ''
    # A list of .NET Framework Assemblies i.e. dlls compiled by a .net language
    env['CSC_REFERENCES'] = ''
    env['_CSC_REFERENCES'] = "${_stripixes('\"/reference:', CSC_REFERENCES, '\"', '', '', __env__)}"
    # A list of paths to search for .NET Framework Assemblies
    env['CSC_LIB_PATHS'] = ''
    env['_CSC_LIB_PATHS'] = "${_stripixes('\"/lib:', CSC_LIB_PATHS, '\"', '', '', __env__)}"
    # Action to build an executable
    env['CSC_ACTION'] = cs_action
    # Action to build a library
    env['CSC_LIB_ACTION'] = cs_lib_action
    
def exists(env):
    return env['CSC']