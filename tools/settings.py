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
from os import path

TOOLS_DIR = path.dirname(path.abspath(__file__)) + os.sep
PROJECT_DIR = path.normpath(path.join(TOOLS_DIR, '../')) + os.sep
BUILD_SCRIPT = TOOLS_DIR + 'build.py'
BUILD_DIR = path.join(PROJECT_DIR, 'build/')
BUILD_LOG = BUILD_DIR + 'build.log'
