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

import os
import subprocess
import sys
from os import path

TOOLS_DIR = path.dirname(path.abspath(__file__))
PROJECT_DIR = path.normpath(path.join(TOOLS_DIR, '../'))
BUILD_SCRIPT = path.join(TOOLS_DIR, 'build.py')
BUILD_DIR = path.join(PROJECT_DIR, 'build/')
BIN_DIR = path.join(BUILD_DIR, 'bin/')
BUILD_LOG = path.join(BUILD_DIR, 'build.log')

def run_check(scriptname, verbose, filename=''):
    script = path.join(TOOLS_DIR, scriptname)
    script_output = subprocess.check_output(script, stderr=subprocess.STDOUT)

    if verbose:
        log_target = sys.stdout
        log_target.write(script_output)
    else:
        if filename:
            log_file = path.join(BUILD_DIR, filename)
            log_target = open(log_file, 'w')
            log_target.write(script_output)
            log_target.close()
