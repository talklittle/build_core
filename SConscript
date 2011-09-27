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

import os

vars = Variables()

# Common build variables
vars.Add(EnumVariable('OS', 'Target OS', 'linux', allowed_values=('linux', 'win7', 'winxp', 'android', 'android_donut', 'maemo', 'darwin')))
vars.Add(EnumVariable('CPU', 'Target CPU', 'x86', allowed_values=('x86', 'x86-64', 'IA64', 'arm', 'x86_bullseye')))
vars.Add(EnumVariable('VARIANT', 'Build variant', 'debug', allowed_values=('debug', 'release')))
vars.Add(EnumVariable('DOCS', '''Output doc type. Setting the doc type to "dev" will produce HTML 
    output that includes all developer files not just the public API.
    ''', 'none', allowed_values=('none', 'pdf', 'html', 'dev')))
vars.Add(EnumVariable('MSVC_VERSION', 'MSVC compiler version - Windows', '9.0', allowed_values=('8.0', '9.0', '10.0')))
vars.Add(EnumVariable('WS', 'Whitespace Policy Checker', 'check', allowed_values=('check', 'detail', 'fix', 'off')))
vars.Add(EnumVariable('JAVAVERSION', '''The version of Java pointed to by the JAVA_HOME
    environment variable. This is not used to select one version of
    the Java comiler vs. another.''', '1.6', allowed_values=('1.5', '1.6')))

# Standard variant directories
build_dir = 'build/${OS}/${CPU}/${VARIANT}'
vars.AddVariables(('OBJDIR', '', build_dir + '/obj'),
                  ('DISTDIR', '', '#' + build_dir + '/dist'))

env = Environment(variables = vars)

# Some tool aren't in default path
if os.environ.has_key('JAVA_HOME'):
    env.PrependENVPath('PATH', os.path.normpath(os.environ['JAVA_HOME'] + '/bin'))
if os.environ.has_key('DOXYGEN_HOME'):
    env.PrependENVPath('PATH', os.path.normpath(os.environ['DOXYGEN_HOME'] + '/bin'))
if os.environ.has_key('GRAPHVIZ_HOME'):
    env.PrependENVPath('PATH', os.path.normpath(os.environ['GRAPHVIZ_HOME'] + '/bin'))
path = env['ENV']['PATH']

# Recreate the environment with the correct path
if env['OS'] == 'win7' or env['OS'] == 'winxp':
    if env['CPU'] == 'x86':
        env = Environment(variables = vars, TARGET_ARCH='x86', MSVC_VERSION='${MSVC_VERSION}', ENV={'PATH': path})
        print 'Building for 32 bit Windows'
    elif env['CPU'] == 'IA64':
        print 'Building for 64 bit Windows'
        env = Environment(variables = vars, TARGET_ARCH='x86_64', MSVC_VERSION='${MSVC_VERSION}', ENV={'PATH': path})
    else:
        print 'Windows CPU must be x86 or IA64'
        Exit()
elif env['OS'] == 'android':
    env = Environment(variables = vars, tools = ['gnulink', 'gcc', 'g++', 'ar', 'as', 'javac', 'javah', 'jar'], ENV={'PATH': path})
else:
    env = Environment(variables = vars, ENV={'PATH': path})

Help(vars.GenerateHelpText(env))

# Validate build vars
if env['OS'] == 'linux':
    env['OS_GROUP'] = 'posix'
    env['OS_CONF'] = 'linux'
elif env['OS'] == 'win7' or env['OS'] == 'winxp':
    env['OS_GROUP'] = 'windows'
    env['OS_CONF'] = 'windows'
elif env['OS'] == 'android':
    env['OS_GROUP'] = 'posix'
    env['OS_CONF'] = 'android'
elif env['OS'] == 'android_donut':
    env['OS_GROUP'] = 'posix'
    env['OS_CONF'] = 'android_donut'
elif env['OS'] == 'maemo':
    env['OS_GROUP'] = 'posix'
    env['OS_CONF'] = 'maemo'
elif env['OS'] == 'darwin':
    env['OS_GROUP'] = 'posix'
    env['OS_CONF'] = 'darwin'
else:
    print 'Unsupported OS/CPU combination'
    Exit()

if env['VARIANT'] == 'release':
    env.Append(CPPDEFINES = 'NDEBUG')

env.Append(CPPDEFINES = ['QCC_OS_GROUP_%s' % env['OS_GROUP'].upper()])

# Setup additional builders
if os.path.exists('tools/scons/doxygen.py'):
    env.Tool('doxygen', toolpath=['tools/scons'])
else:
    def dummy_emitter(target, source, env):
        return [], []
    def dummy_action(target, source, env):
        pass
    dummyBuilder = Builder(action = dummy_action,
                           emitter = dummy_emitter);
    env.Append(BUILDERS = {'Doxygen' : dummyBuilder})
env.Tool('genversion', toolpath=['tools/scons'])
env.Tool('javadoc', toolpath=['tools/scons'])

# Create the builder that generates Status.h from Status.xml
import sys
import SCons.Util
sys.path.append('tools/bin')
import make_status
def status_emitter(target, source, env):
    base,ext = SCons.Util.splitext(str(target[0]))
    target.append('inc/' + os.path.basename(base + '.h'))
    return target, source

def status_action(target, source, env):
    base,ext = SCons.Util.splitext(str(target[0]))
    cfile = target[0]
    hfile = target[1]
    base,rest = str(hfile).rsplit('inc' + os.path.sep)
    return make_status.main(['--base=%s' % base,
                             '--code=%s' % cfile,
                             '--header=%s' % hfile,
                             str(source[0])])


statusBuilder = Builder(action = status_action,
                        emitter = status_emitter,
                        suffix = '.c',
                        src_suffix = '.xml')
env.Append(BUILDERS = {'Status' : statusBuilder})

# Read OS and CPU specific SConscript file
Export('env')
env.SConscript('conf/${OS_CONF}/${CPU}/SConscript')

# Whitespace policy
if env['WS'] != 'off' and not env.GetOption('clean'):
    import sys
    sys.path.append('tools/bin')
    import whitespace

    def wsbuild(target, source, env):
        print "Evaluating whitespace compliance..."
        print "Note: enter 'scons -h' to see whitespace (WS) options"
        return whitespace.main([env['WS'],])

    env.Command('#/ws', Dir('$DISTDIR'), wsbuild)

Return('env')
