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

# This doxygen builder does not parse the input file and populate the file list
# using an emmitter for this reason to use this builder it is best to specify
# env.Doxygen(source='<doxygen_config_file>', target=Dir('tmp')) 
#    Where the tmp directory is never created meaning that doxygen is run every
#    time the SCons is run
# env.Clean('Doxygen_html', Dir('html'))
#    Where 'html' is the output directory if building latex the output directory 
#    would be latex 

def generate(env):
    # Add Builders for the Doxygen documentation tool
    import SCons.Builder
    doxygen_builder = SCons.Builder.Builder(
        action = "cd ${SOURCE.dir}  &&  ${DOXYGEN} ${SOURCE.file}",
    )

    env.Append(BUILDERS = {
        'Doxygen': doxygen_builder,
    })

    env.AppendUnique(
        DOXYGEN = 'doxygen',
    )

def exists(env):
    """
    Make sure doxygen exists.
    """
    return env.Detect("doxygen")