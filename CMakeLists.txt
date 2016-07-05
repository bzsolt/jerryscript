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
project (Jerry C ASM)

# Determining platform
 set(PLATFORM "${CMAKE_SYSTEM_NAME}")
 string(TOUPPER "${PLATFORM}" PLATFORM)

# Remove rdynamic option
 set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS )

# Components
 set(BUILD_JERRY_CORE  ON  CACHE BOOL "Build jerry-core?")
 set(BUILD_JERRY_LIBC  ON  CACHE BOOL "Build jerry-libc?")
 set(BUILD_JERRY_LIBM  ON  CACHE BOOL "Build jerry-libm?")
 set(BUILD_JERRY       ON  CACHE BOOL "Build jerry command line tool?")
 set(BUILD_UNITTESTS   OFF CACHE BOOL "Build unit tests?")

# Optional build settings
 set(USE_PORT_DIR              "DEFAULT"   CACHE STRING "Should we use default or external port?")
 set(USE_LIBC                  "JERRY"     CACHE STRING "should we use jerry-libc, compiler-default or external libc?")
 set(ENABLE_LTO                OFF         CACHE BOOL   "Enable LTO build?")
 set(ENABLE_ALL_IN_ONE         ON          CACHE BOOL   "Enable all-in-one build?")
 set(ENABLE_STRIP              ON          CACHE BOOL   "Discards all symbols from object files?")
 set(EXTERNAL_LIBS_INTERFACE   "UNDEFINED" CACHE STRING "Path to external libraries' include directory")

 if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
 endif()

 if("${PLATFORM}" STREQUAL "DARWIN")
  set(ENABLE_LTO "OFF")
  set(ENABLE_ALL_IN_ONE "ON")
 endif()

 # Status messages
 message(STATUS "CMAKE_SYSTEM_NAME         " ${CMAKE_SYSTEM_NAME})
 message(STATUS "CMAKE_SYSTEM_PROCESSOR    " ${CMAKE_SYSTEM_PROCESSOR})
 message(STATUS "CMAKE_BUILD_TYPE          " ${CMAKE_BUILD_TYPE})
 message(STATUS "BUILD_JERRY_CORE          " ${BUILD_JERRY_CORE})
 message(STATUS "BUILD_JERRY_LIBC          " ${BUILD_JERRY_LIBC})
 message(STATUS "BUILD_JERRY_LIBM          " ${BUILD_JERRY_LIBM})
 message(STATUS "BUILD_JERRY               " ${BUILD_JERRY})
 message(STATUS "BUILD_UNITTESTS           " ${BUILD_UNITTESTS})
 message(STATUS "USE_PORT_DIR              " ${USE_PORT_DIR})
 message(STATUS "USE_LIBC                  " ${USE_LIBC})
 message(STATUS "ENABLE_LTO                " ${ENABLE_LTO})
 message(STATUS "ENABLE_ALL_IN_ONE         " ${ENABLE_ALL_IN_ONE})
 message(STATUS "ENABLE_STRIP              " ${ENABLE_STRIP})
 message(STATUS "EXTERNAL_LIBS_INTERFACE   " ${EXTERNAL_LIBS_INTERFACE})

# Setup directories
 # Project binary dir
 set(PROJECT_BINARY_DIR ${CMAKE_BINARY_DIR})

 # Library output directory
 set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

 # Executable output directory
 set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin/)

 # Archive targets output Directory
 set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

# Compile/link flags
 # build mode specific compile/link flags

 if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  if(BUILD_UNITTESTS STREQUAL "ON")
   set(CMAKE_C_FLAGS_DEBUG "-O3")
  endif()
 else()
   set(CMAKE_C_FLAGS_RELEASE "-Os")
 endif()

 # Architecture-specific compile/link flags
  foreach(FLAG ${FLAGS_COMMON_ARCH})
   set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${FLAG}")
   set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${FLAG}")
  endforeach()

 if (NOT "${PLATFORM}" MATCHES "^(LINUX|DARWIN|EXTERNAL|OPENWRT)$")
  message(FATAL_ERROR "Platform '${PLATFORM}' is not supported")
 endif()

 #Should we use external libc?
 if(NOT ${USE_LIBC} STREQUAL "COMPILER" AND NOT ${USE_LIBC} STREQUAL "JERRY")
  if(NOT EXISTS "${USE_LIBC}/stdlib.h")
   message(FATAL_ERROR "It seems that external libc interface '${USE_LIBC}' doesn't provide stdlib.h header")
  endif()
  set(INCLUDE_LIBC_INTERFACE ${USE_LIBC})
 elseif (${USE_LIBC} STREQUAL "JERRY")
  set(INCLUDE_LIBC_INTERFACE ${CMAKE_SOURCE_DIR}/jerry-libc/include)
 endif()

 if(CMAKE_COMPILER_IS_GNUCC)
  if(ENABLE_LTO)
   # Use gcc-ar and gcc-ranlib to support LTO
   set (CMAKE_AR "gcc-ar")
   set(CMAKE_RANLIB "gcc-ranlib")
  endif()
 endif()

 # should we use default or external port?
 if (${USE_PORT_DIR} STREQUAL "DEFAULT")
  set(PORT_DIR ${CMAKE_SOURCE_DIR}/targets/default)
  if (${USE_LIBC} STREQUAL "COMPILER")
   set(DEFINES_JERRY ${DEFINES_JERRY} _BSD_SOURCE)
  endif()
 else()
   set(PORT_DIR ${USE_PORT_DIR})
 endif()

# Are there any interfaces for external libraries, other than libc, that should be registered?
 if(NOT EXTERNAL_LIBS_INTERFACE STREQUAL "UNDEFINED")
  foreach(EXTERNAL_LIB_INTERFACE ${EXTERNAL_LIBS_INTERFACE})
   if (NOT EXISTS "${EXTERNAL_LIB_INTERFACE}")
    message(FATAL_ERROR "Interface directory of the external library doesn't exist: ${EXTERNAL_LIB_INTERFACE}")
   endif()
   set(INCLUDE_EXTERNAL_LIBS_INTERFACE ${INCLUDE_EXTERNAL_LIBS_INTERFACE} ${EXTERNAL_LIB_INTERFACE})
  endforeach()
 endif()

# Compiler / Linker flags
 set(COMPILE_FLAGS_COMMON "-fno-builtin")
 if(NOT ("${PLATFORM}" STREQUAL "DARWIN"))
  set(LINKER_FLAGS_COMMON "-Wl,-z,noexecstack")
 else()
  set(LINKER_FLAGS_COMMON "-lSystem")
 endif()

 # Turn off linking to compiler's default libc, in case jerry-libc or external is used
 if(NOT USE_LIBC STREQUAL "COMPILER")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -nostdlib")
 endif()

 # LTO
  if(ENABLE_LTO)
   set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} -flto")
   if(NOT ("${PLATFORM}" STREQUAL "DARWIN") AND CMAKE_COMPILER_IS_GNUCC)
    set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} -fno-fat-lto-objects")
   endif()
   set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -flto")
  endif()

 # Turn off stack protector
  set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} -fno-stack-protector")

 # Debug information
  set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} -g -gdwarf-4")

  macro(add_jerry_compile_flags)
    foreach(_flag ${ARGV})
      set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} ${_flag}")
    endforeach()
  endmacro()

  macro(add_jerry_compile_warnings)
    foreach(_warning ${ARGV})
      add_jerry_compile_flags(-W${_warning})
      if(CMAKE_COMPILER_IS_GNUCC)
        add_jerry_compile_flags(-Werror=${_warning})
      endif()
    endforeach()
  endmacro()

  add_jerry_compile_warnings(all extra format-nonliteral init-self conversion sign-conversion format-security missing-declarations)
  add_jerry_compile_flags(-Wno-stack-protector -Wno-attributes)
  if(CMAKE_COMPILER_IS_GNUCC)
    if(${USE_LIBC} STREQUAL "JERRY")
      add_jerry_compile_flags(-Werror)
    endif()
    add_jerry_compile_warnings(logical-op)
  else()
    add_jerry_compile_flags(-Wno-nested-anon-types)
  endif()

  if(DEFINED EXTERNAL_COMPILE_FLAGS)
    foreach(FLAG ${EXTERNAL_COMPILE_FLAGS})
      set(COMPILE_FLAGS_COMMON "${COMPILE_FLAGS_COMMON} ${FLAG}")
    endforeach()
  endif()

  if(DEFINED EXTERNAL_LINKER_FLAGS)
    foreach(FLAG ${EXTERNAL_LINKER_FLAGS})
      set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${FLAG}")
    endforeach()
  endif()

 # Static build
  if(NOT ("${PLATFORM}" STREQUAL "DARWIN"))
   set(LINKER_FLAGS_STATIC "-static")
  endif()

 # C
  set(C_FLAGS_COMMON "-std=c99 -pedantic")

# Strip binary
 if(ENABLE_STRIP AND NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -s")
 endif()

# Jerry's libc
 if(BUILD_JERRY_LIBC STREQUAL "ON")
  add_subdirectory(jerry-libc)
 endif()

# Jerry's libm
 if (BUILD_JERRY_LIBM STREQUAL "ON")
  add_subdirectory(jerry-libm)
 endif()

 # Jerry's core
 if(BUILD_JERRY_CORE STREQUAL "ON")
  add_subdirectory(jerry-core)
 endif()

# Jerry commandline tool
 if (BUILD_JERRY STREQUAL "ON")
  add_subdirectory(jerry-main)
endif()

# Unittests
 if (BUILD_UNITTESTS STREQUAL "ON")
  add_subdirectory(tests/unit)
 endif()