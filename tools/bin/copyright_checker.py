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
import re
import os.path

usage = "copyright_checker.py <file to check>"

copyregex = re.compile('[\s\*\#]*Copyright (\(c\)\s?)?\d{4}(\s?-\s?\d{4})?, Qualcomm Innovation Center, Inc.?' +
	        '[\s\*\#]*Licensed under the Apache License, Version 2.0 \(the \"License\"\)\;' +
	        '[\s\*\#]*you may not use this file except in compliance with the License.' +
	        # The following two lines do not appear in some files (e.g. NOTICE).  
	        # We are considering this to be valid for the time being.
	        '([\s\*\#]*You may obtain a copy of the License at)?' + 
	        '([\s\*\#]*http:\/\/www.apache.org\/licenses\/LICENSE-2.0)?' +
	        '[\s\*\#]*Unless required by applicable law or agreed to in writing, software' +
	        '[\s\*\#]*distributed under the License is distributed on an \"AS IS\" BASIS,' +
	        '[\s\*\#]*WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.' +
	        '[\s\*\#]*See the License for the specific language governing permissions and' +
	        '[\s\*\#]*limitations under the License')

if len(sys.argv) < 2:
    print "Requires a valid filename argmument"
    print usage
    sys.exit(-1)

def main():
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1]) as x: f = x.read()
    else:
        print sys.argv[1] + " does not exist or is not a file"
        print usage
        sys.exit(-1)

    if copyregex.search(f):
        sys.exit(0)
    else:
        # print sys.argv[1]
        sys.exit(1)

if __name__ == "__main__":
    main()
    

