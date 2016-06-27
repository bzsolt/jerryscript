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
import os
import subprocess
import sys
from os import path

def join_path(pathes):
    return path.abspath(reduce(lambda x, y: path.join(x, y), pathes))

SCRIPT_PATH = path.dirname(path.abspath(__file__))
PROJECT_DIR = join_path([SCRIPT_PATH, '../'])
BUILD_DIR = join_path([PROJECT_DIR, 'tmp/'])

def add_build_args(parser):
    parser.add_argument('-v', '--verbose', help='Increase verbosity', action='store_true', dest='verbose')
    parser.add_argument('--all-in-one', help='All-in-one build', action='store_true', dest='build_all_in_one')
    parser.add_argument('--debug', help='Debug build', action='store_true', dest='build_debug')
    # parser.add_argument('--not stripped')

def get_arguments():
    parser = argparse.ArgumentParser()
    add_build_args(parser)

    return parser.parse_args()

def generate_build_options(arguments):
    build_options = []

    if arguments.verbose:
        build_options.append('-DCMAKE_VERBOSE_MAKEFILE=ON')

    if arguments.build_all_in_one:
        build_options.append('-DENABLE_ALL_IN_ONE=ON')

    if arguments.build_debug:
        build_options.append('-DENABLE_DEBUG=ON')

    return build_options

def configure_build(arguments):
    if not os.path.exists(BUILD_DIR):
        makedirs(BUILD_DIR)

    build_options = generate_build_options(arguments)

    return subprocess.call(['cmake', '-B' + BUILD_DIR, '-H' + PROJECT_DIR] + build_options)

def build_jerry(arguments):
    return subprocess.call(['make', '-s', '-C', BUILD_DIR])

def print_result(ret):
    print('=' * 30)
    if ret:
        print('Build failed with exit code: %s' % (ret))
    else:
        print('Build succeeded!')
    print('=' * 30)

def main():
    arguments = get_arguments()
    ret = configure_build(arguments)

    if not ret:
        ret = build_jerry(arguments)

    print_result(ret)
    sys.exit(ret)


if __name__ == "__main__":
    main()
