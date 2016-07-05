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
from os import makedirs
from settings import *

def add_build_args(parser):
    parser.add_argument('--verbose', '-v', action='store_const', const='ON', default='OFF', help='Increase verbosity')
    parser.add_argument('--unittests', action='store_const', const='ON', default='OFF', help='Build unittests')
    parser.add_argument('--clean', action='store_true', default=False, help='Clean build')
    parser.add_argument('--strip', choices=['on', 'off'], default='on', help='Strip release binary (default: %(default)s)')
    parser.add_argument('--all-in-one', choices=['on', 'off'], default='off', help='All-in-one build (default: %(default)s)')
    parser.add_argument('--debug', action='store_const', const='Debug', default='Release', help='Debug build')
    parser.add_argument('--lto', choices=['on', 'off'], default='on', help='Enable link-time optimizations (default: %(default)s)')
    parser.add_argument('--profile', choices=['full', 'compact', 'minimal'], default='full', help='Specify the ECMAScript profile (default: %(default)s)')
    parser.add_argument('--error-messages', choices=['on', 'off'], default='off', help='Enable error messages (default: %(default)s)')
    parser.add_argument('--log', choices=['on', 'off'], default='off', help='Enable logging (default: %(default)s)')
    parser.add_argument('--valgrind', choices=['on', 'off'], default='off', help='Enable Valgrind support (default: %(default)s)')
    parser.add_argument('--valgrind-freya', choices=['on', 'off'], default='off', help='Enable Valgrind-Freya support (default: %(default)s)')
    parser.add_argument('--mem-stats', choices=['on', 'off'], default='off', help='Enable memory-statistics (default: %(default)s)')
    parser.add_argument('--mem-stress-test', choices=['on', 'off'], default='off', help='Enable mem-stress test (default: %(default)s)')
    parser.add_argument('--cmake-param', action='append', default=[], help='Add custom arguments to CMake')
    parser.add_argument('--compile-flag', action='append', default=[], help='Add custom compile flag')
    parser.add_argument('--linker-flag', action='append', default=[], help='Add custom linker flag')
    parser.add_argument('--toolchain', action='store', default='', help='Add toolchain file')

    # TODO: Allow to switch between default and jerry libc

def get_arguments():
    parser = argparse.ArgumentParser()
    add_build_args(parser)

    return parser.parse_args()

def generate_build_options(arguments):
    build_options = []

    build_options.append('-DCMAKE_VERBOSE_MAKEFILE=%s' % arguments.verbose)
    build_options.append('-DCMAKE_BUILD_TYPE=%s' % arguments.debug)
    build_options.append('-DFEATURE_PROFILE=%s' % arguments.profile)
    build_options.append('-DFEATURE_ERROR_MESSAGES=%s' % arguments.error_messages)
    build_options.append('-DFEATURE_LOG=%s' % arguments.log)
    build_options.append('-DFEATURE_VALGRIND=%s' % arguments.valgrind)
    build_options.append('-DFEATURE_VALGRIND_FREYA=%s' % arguments.valgrind_freya)
    build_options.append('-DFEATURE_MEM_STATS=%s' % arguments.mem_stats)
    build_options.append('-DFEATURE_MEM_STRESS_TEST=%s' % arguments.mem_stress_test)
    build_options.append('-DENABLE_ALL_IN_ONE=%s' % arguments.all_in_one.upper())
    build_options.append('-DENABLE_LTO=%s' % arguments.lto.upper())
    build_options.append('-DENABLE_STRIP=%s' % arguments.strip.upper())
    build_options.append('-DBUILD_UNITTESTS=%s' % arguments.unittests)

    build_options.extend(arguments.cmake_param)
    build_options.append('-DEXTERNAL_COMPILE_FLAGS=' + ' '.join(arguments.compile_flag))
    build_options.append('-DEXTERNAL_LINKER_FLAGS=' + ' '.join(arguments.linker_flag))

    if arguments.toolchain:
        build_options.append('-DCMAKE_TOOLCHAIN_FILE=%s' % arguments.toolchain)

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
