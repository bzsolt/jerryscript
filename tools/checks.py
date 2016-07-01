#!/usr/bin/env python

# Copyright 2016 Samsung Electronics Co., Ltd.
# Copyright 2016 University of Szeged.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import subprocess
import sys
from settings import *

optparser = argparse.ArgumentParser()
optparser.add_argument('-v', '--verbose', action='store_true', default=False, help='increase verbosity')
args = optparser.parse_args()

def run_check(scriptname, filename=''):
    script = TOOLS_DIR + scriptname
    script_output = subprocess.check_output(script, stderr=subprocess.STDOUT)

    if args.verbose:
        log_target = sys.stdout
        log_target.write(script_output)
    else:
        if filename:
            log_file = path.normpath(BUILD_DIR + filename)
            log_target = open(log_file, 'w')
            log_target.write(script_output)


run_check('check-signed-off.sh')
run_check('check-vera.sh', 'vera.log')
run_check('check-cppcheck.sh', 'cppcheck.log')
