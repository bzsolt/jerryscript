# Copyright 2015-2016 Samsung Electronics Co., Ltd.
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
set(JERRY_CORE_NAME    jerry-core)
project (${JERRY_CORE_NAME} C ASM)

# Optional features
set(FEATURE_PROFILE         "full" CACHE STRING "ES5.1 profile: full, compact, minimal")
set(FEATURE_ERROR_MESSAGES  OFF    CACHE BOOL   "Enable error messages?")
set(FEATURE_LOG             OFF    CACHE BOOL   "Enable logging?")
set(FEATURE_VALGRIND        OFF    CACHE BOOL   "Enable Valgrind support?")
set(FEATURE_VALGRIND_FREYA  OFF    CACHE BOOL   "Enable Valgrind-Freya support?")
set(FEATURE_MEM_STRESS_TEST OFF    CACHE BOOL   "Enable mem-stress test?")
set(FEATURE_MEM_STATS       OFF    CACHE BOOL   "Enable memory-statistics?")
set(MEM_HEAP_SIZE_KB        "512"  CACHE STRING "Size of memory heap, in kilobytes")

# Status messages
message(STATUS "FEATURE_PROFILE           " ${FEATURE_PROFILE})
message(STATUS "FEATURE_ERROR_MESSAGES    " ${FEATURE_ERROR_MESSAGES})
message(STATUS "FEATURE_LOG               " ${FEATURE_LOG})
message(STATUS "FEATURE_VALGRIND          " ${FEATURE_VALGRIND})
message(STATUS "FEATURE_VALGRIND_FREYA    " ${FEATURE_VALGRIND_FREYA})
message(STATUS "FEATURE_MEM_STRESS_TEST   " ${FEATURE_MEM_STRESS_TEST})
message(STATUS "FEATURE_MEM_STATS         " ${FEATURE_MEM_STATS})
message(STATUS "MEM_HEAP_SIZE_KB          " ${MEM_HEAP_SIZE_KB})

# Definitions
# Size of heap
math(EXPR MEM_HEAP_AREA_SIZE "${MEM_HEAP_SIZE_KB} * 1024")
set(DEFINES_JERRY ${DEFINES_JERRY} CONFIG_MEM_HEAP_AREA_SIZE=${MEM_HEAP_AREA_SIZE})

# Get version information from git
if(IS_DIRECTORY "${CMAKE_SOURCE_DIR}/.git")
  execute_process(COMMAND git symbolic-ref -q HEAD
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                  OUTPUT_VARIABLE JERRY_GIT_BRANCH
                  OUTPUT_STRIP_TRAILING_WHITESPACE)
  execute_process(COMMAND git rev-parse HEAD
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                  OUTPUT_VARIABLE JERRY_GIT_COMMIT
                  OUTPUT_STRIP_TRAILING_WHITESPACE)
else()
  set(JERRY_GIT_BRANCH "UNDEFINED")
  set(JERRY_GIT_COMMIT "UNDEFINED")
endif()

# Get build date
execute_process(COMMAND date +%d/%m/%Y
                OUTPUT_VARIABLE JERRY_BUILD_DATE
                OUTPUT_STRIP_TRAILING_WHITESPACE)

set(DEFINES_JERRY
    ${DEFINES_JERRY}
    JERRY_ENABLE_SNAPSHOT_SAVE
    JERRY_ENABLE_SNAPSHOT_EXEC
    JERRY_BUILD_DATE="${JERRY_BUILD_DATE}"
    JERRY_COMMIT_HASH="${JERRY_GIT_COMMIT}"
    JERRY_BRANCH_NAME="${JERRY_GIT_BRANCH}")

# build mode specific compile/link flags
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_ENABLE_PRETTY_PRINTER)
else()
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_NDEBUG)
endif()

# ES5.1 profiles
# Full profile
if(FEATURE_PROFILE STREQUAL "full")
  set(DEFINES_JERRY ${DEFINES_JERRY} CONFIG_ECMA_NUMBER_TYPE=CONFIG_ECMA_NUMBER_FLOAT64)

# Compact profile
elseif(FEATURE_PROFILE STREQUAL "compact")
  set(DEFINES_JERRY ${DEFINES_JERRY} CONFIG_ECMA_COMPACT_PROFILE)

# Minimal compact profile
elseif(FEATURE_PROFILE STREQUAL "minimal")
  set(DEFINES_JERRY
      ${DEFINES_JERRY}
      CONFIG_ECMA_COMPACT_PROFILE
#
# Date and RegExp built-in objects are also disabled in non-minimal compact profile build
#
# CONFIG_ECMA_COMPACT_PROFILE_DISABLE_DATE_BUILTIN
# CONFIG_ECMA_COMPACT_PROFILE_DISABLE_REGEXP_BUILTIN
#
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_NUMBER_BUILTIN
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_STRING_BUILTIN
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_BOOLEAN_BUILTIN
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_ERROR_BUILTINS
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_ARRAY_BUILTIN
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_MATH_BUILTIN
      CONFIG_ECMA_COMPACT_PROFILE_DISABLE_JSON_BUILTIN)

else()
  message(FATAL_ERROR "FEATURE_PROFILE='${FEATURE_PROFILE}' doesn't supported")
endif()

# Include directories
set(INCLUDE_CORE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/lit
    ${CMAKE_CURRENT_SOURCE_DIR}/rcs
    ${CMAKE_CURRENT_SOURCE_DIR}/jmem
    ${CMAKE_CURRENT_SOURCE_DIR}/vm
    ${CMAKE_CURRENT_SOURCE_DIR}/ecma/builtin-objects
    ${CMAKE_CURRENT_SOURCE_DIR}/ecma/base
    ${CMAKE_CURRENT_SOURCE_DIR}/ecma/operations
    ${CMAKE_CURRENT_SOURCE_DIR}/parser/js
    ${CMAKE_CURRENT_SOURCE_DIR}/parser/regexp
    ${CMAKE_CURRENT_SOURCE_DIR}/jrt)

# Sources
# Jerry core
file(GLOB SOURCE_CORE_API                   *.c)
file(GLOB SOURCE_CORE_LIT                   lit/*.c)
file(GLOB SOURCE_CORE_RCS                   rcs/*.c)
file(GLOB SOURCE_CORE_MEM                   jmem/*.c)
file(GLOB SOURCE_CORE_VM                    vm/*.c)
file(GLOB SOURCE_CORE_ECMA_BUILTINS         ecma/builtin-objects/*.c)
file(GLOB SOURCE_CORE_ECMA_BASE             ecma/base/*.c)
file(GLOB SOURCE_CORE_ECMA_OPERATIONS       ecma/operations/*.c)
file(GLOB SOURCE_CORE_PARSER_JS             parser/js/*.c)
file(GLOB SOURCE_CORE_PARSER_REGEXP         parser/regexp/*.c)
file(GLOB SOURCE_CORE_JRT                   jrt/*.c)

set(SOURCE_CORE_FILES
    ${SOURCE_CORE_API}
    ${SOURCE_CORE_LIT}
    ${SOURCE_CORE_RCS}
    ${SOURCE_CORE_MEM}
    ${SOURCE_CORE_VM}
    ${SOURCE_CORE_ECMA_BUILTINS}
    ${SOURCE_CORE_ECMA_BASE}
    ${SOURCE_CORE_ECMA_OPERATIONS}
    ${SOURCE_CORE_PARSER_JS}
    ${SOURCE_CORE_PARSER_REGEXP}
    ${SOURCE_CORE_JRT})

# Jerry port
file(GLOB SOURCE_PORT_FILES ${PORT_DIR}/*.c)

# All-in-one build
if("${ENABLE_ALL_IN_ONE}" STREQUAL "ON")
  set(ALL_IN_FILE "${CMAKE_BINARY_DIR}/jerry-all-in.c")
  list(SORT SOURCE_CORE_FILES)
  file(REMOVE ${ALL_IN_FILE})

  foreach(FILE ${SOURCE_CORE_FILES})
    file(APPEND ${ALL_IN_FILE} "#include \"${FILE}\"\n")
  endforeach()

  foreach(FILE ${SOURCE_PORT_FILES})
    file(APPEND ${ALL_IN_FILE} "#include \"${FILE}\"\n")
  endforeach()

  set(SOURCE_CORE ${ALL_IN_FILE} ${SOURCE_PORT_FILES})
else()
  set(SOURCE_CORE ${SOURCE_CORE_FILES} ${SOURCE_PORT_FILES})
endif()

# Per-option configuration
# Memory management stress-test mode
if("${FEATURE_MEM_STRESS_TEST}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} JMEM_GC_BEFORE_EACH_ALLOC)
endif()

# Memory statistics
if("${FEATURE_MEM_STATS}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} JMEM_STATS)
endif()

# Third-party
# Valgrind
set(INCLUDE_THIRD_PARTY_VALGRIND ${CMAKE_SOURCE_DIR}/third-party/valgrind)

# Valgrind
if("${FEATURE_VALGRIND}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} ${JERRY_VALGRIND})
  set(INCLUDE_CORE ${INCLUDE_CORE} ${INCLUDE_THIRD_PARTY_VALGRIND})
endif()

# Valgrind Freya
if("${FEATURE_VALGRIND_FREYA}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_VALGRIND_FREYA)
  set(INCLUDE_CORE ${INCLUDE_CORE} ${INCLUDE_THIRD_PARTY_VALGRIND})
endif()

# JERRY_HEAP_SECTION_ATTR
if(DEFINED JERRY_HEAP_SECTION_ATTR)
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_HEAP_SECTION_ATTR=${JERRY_HEAP_SECTION_ATTR})
endif()

# Log
if("${FEATURE_LOG}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_ENABLE_LOG)
endif()

# Fill error messages for builtin error objects
if("${FEATURE_ERROR_MESSAGES}" STREQUAL "ON")
  set(DEFINES_JERRY ${DEFINES_JERRY} JERRY_ENABLE_ERROR_MESSAGES)
endif()

# C
if(NOT DEFINED C_FLAGS_COMMON)
  set(C_FLAGS_COMMON "-std=c99 -pedantic")
endif()

add_library(${JERRY_CORE_NAME} STATIC ${SOURCE_CORE})
set_property(TARGET ${JERRY_CORE_NAME}
             PROPERTY COMPILE_FLAGS "${C_FLAGS_COMMON} ${COMPILE_FLAGS_COMMON}")
target_compile_definitions(${JERRY_CORE_NAME} PRIVATE ${DEFINES_JERRY})
target_include_directories(${JERRY_CORE_NAME} PRIVATE ${INCLUDE_CORE})
target_include_directories(${JERRY_CORE_NAME} SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
target_include_directories(${JERRY_CORE_NAME} SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})

target_compile_definitions(${JERRY_CORE_NAME} INTERFACE ${DEFINES_JERRY})
target_include_directories(${JERRY_CORE_NAME} INTERFACE ${INCLUDE_CORE})
