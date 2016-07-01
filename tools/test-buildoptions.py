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
from settings import *

optparser = argparse.ArgumentParser()
optparser.add_argument('-v', '--verbose', action='store_true', default=False, help='increase verbosity')
args = optparser.parse_args()

# TODO: Should add a flag for COMPILER_DEFAULT_LIBC
option_list = ['--lto', '--log', '--error-messages', '--all-in-one', '--valgrind', '--valgrind-freya'];

for option in option_list:
    script_output = subprocess.check_output([BUILD_SCRIPT, option, 'on', '--clean', '--unittests', '-v'], stderr=subprocess.STDOUT)

    if args.verbose:
        log_target = sys.stdout
    else:
        log_target = open(BUILD_LOG, 'w')

    log_target.write(script_output)
