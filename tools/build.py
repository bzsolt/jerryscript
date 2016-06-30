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
from os import makedirs

def join_path(pathes):
    return path.abspath(reduce(lambda x, y: path.join(x, y), pathes))

SCRIPT_PATH = path.dirname(path.abspath(__file__))
PROJECT_DIR = join_path([SCRIPT_PATH, '../'])
BUILD_DIR = join_path([PROJECT_DIR, 'tmp/'])

def add_build_args(parser):
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Increase verbosity')
    parser.add_argument('--unittests', action='store_true', default=False, help='Build unittests')
    parser.add_argument('--clean', action='store_true', default=False, help='Clean build')
    parser.add_argument('--all-in-one', choices=['on', 'off'], default='off', help='All-in-one build (default: %(default)s)')
    parser.add_argument('--debug', choices=['on', 'off'], default='off', help='Debug build (default: %(default)s)')
    parser.add_argument('--lto', choices=['on', 'off'], default='on', help='Enable link-time optimizations (default: %(default)s)')
    parser.add_argument('--profile', choices=['full', 'compact', 'minimal'], default='full', help='Specify the ECMAScript profile (default: %(default)s)')
    parser.add_argument('--error-messages', choices=['on', 'off'], default='off', help='Enable error messages (default: %(default)s)')
    parser.add_argument('--log', choices=['on', 'off'], default='off', help='Enable logging (default: %(default)s)')
    parser.add_argument('--valgrind', choices=['on', 'off'], default='off', help='Enable Valgrind support (default: %(default)s)')
    parser.add_argument('--valgrind-freya', choices=['on', 'off'], default='off', help='Enable Valgrind-Freya support (default: %(default)s)')
    parser.add_argument('--mem-stats', choices=['on', 'off'], default='off', help='Enable memory-statistics (default: %(default)s)')
    parser.add_argument('--mem-stress-test', choices=['on', 'off'], default='off', help='Enable mem-stress test (default: %(default)s)')
    parser.add_argument('--cmake-param', action='append', help='Add custom arguments to CMake')
    parser.add_argument('--compile-flag', action='append', help='Add custom compile flag')
    parser.add_argument('--linker-flag', action='append', help='Add custom linker flag')

    # TODO: parser.add_argument('--not stripped')

def get_arguments():
    parser = argparse.ArgumentParser()
    add_build_args(parser)

    return parser.parse_args()

def args_or_empty_list(arguments):
    return (arguments if arguments else [])

def generate_build_options(arguments):
    build_options = []

    build_options.append('-DCMAKE_VERBOSE_MAKEFILE=%s' % ('ON' if arguments.verbose else 'OFF'))
    build_options.append('-DFEATURE_PROFILE=%s' % arguments.profile)
    build_options.append('-DFEATURE_ERROR_MESSAGES=%s' % arguments.error_messages)
    build_options.append('-DFEATURE_LOG=%s' % arguments.log)
    build_options.append('-DFEATURE_VALGRIND=%s' % arguments.valgrind)
    build_options.append('-DFEATURE_VALGRIND_FREYA=%s' % arguments.valgrind_freya)
    build_options.append('-DFEATURE_MEM_STATS=%s' % arguments.mem_stats)
    build_options.append('-DFEATURE_MEM_STRESS_TEST=%s' % arguments.mem_stress_test)
    build_options.append('-DENABLE_ALL_IN_ONE=%s' % arguments.all_in_one.upper())
    build_options.append('-DENABLE_DEBUG=%s' % arguments.debug.upper())
    build_options.append('-DENABLE_LTO=%s' % arguments.lto.upper())
    build_options.append('-DBUILD_UNITTESTS=%s' % ('ON' if arguments.unittests else 'OFF'))

    build_options.extend(args_or_empty_list(arguments.cmake_param))
    build_options.append('-DUSER_DEFINED_COMPILE_FLAGS=' + ' '.join(args_or_empty_list(arguments.compile_flag)))
    build_options.append('-DUSER_DEFINED_LINKER_FLAGS=' + ' '.join(args_or_empty_list(arguments.linker_flag)))

    return build_options

def configure_build(arguments):
    if not os.path.exists(BUILD_DIR):
        makedirs(BUILD_DIR)

    build_options = generate_build_options(arguments)

    cmakeCmd = ['cmake', '-B' + BUILD_DIR, '-H' + PROJECT_DIR]
    cmakeCmd.extend(build_options)

    return subprocess.call(cmakeCmd)

def build_jerry(arguments):
    if arguments.clean:
        subprocess.call(['make', '--no-print-directory', '-C', BUILD_DIR, 'clean'])

    return subprocess.call(['make', '--no-print-directory', '-C', BUILD_DIR])

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
