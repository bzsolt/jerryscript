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

cmake_minimum_required (VERSION 2.8.12)
set(JERRY_DEBUGGER_NAME jerry-debugger)
project (${JERRY_DEBUGGER_NAME} C)

 # Compiler / linker flags
set(COMPILE_FLAGS_DEBUGGER "${COMPILE_FLAGS_COMMON} ${C_FLAGS_COMMON}")
set(CMAKE_C_FLAGS "-D_GNU_SOURCE -DPARSER_DEBUG")

# Include directories
 set(INCLUDE_DEBUGGER ${CMAKE_SOURCE_DIR}/jerry-debugger)

# Source directories
file(GLOB SOURCE_DEBUGGER *.c)

add_library(${JERRY_DEBUGGER_NAME} STATIC ${SOURCE_DEBUGGER})
set_property(TARGET ${JERRY_DEBUGGER_NAME}
             PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_DEBUGGER}")

target_include_directories(${JERRY_DEBUGGER_NAME} PRIVATE ${INCLUDE_DEBUGGER})
target_include_directories(${JERRY_DEBUGGER_NAME} INTERFACE ${INCLUDE_DEBUGGER})
