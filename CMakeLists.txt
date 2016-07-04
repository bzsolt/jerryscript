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
 set(USE_PORT_DIR      "DEFAULT" CACHE STRING "Should we use default or external port?")
 set(USE_LIBC          "JERRY"   CACHE STRING "should we use jerry-libc, compiler-default or external libc?")
 set(ENABLE_LTO        OFF       CACHE BOOL   "Enable LTO build?")
 set(ENABLE_ALL_IN_ONE ON        CACHE BOOL   "Enable all-in-one build?")

# Compile/link flags
 # build mode specific compile/link flags
 if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  if(BUILD_UNITTESTS STREQUAL "ON")
   set(CMAKE_C_FLAGS "-O3")
  endif()
 elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
  set(CMAKE_C_FLAGS "-Os")
 endif()

# Architecture-specific compile/link flags
 foreach(FLAG ${FLAGS_COMMON_ARCH})
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${FLAG}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${FLAG}")
 endforeach()

# Setup directories
 # Project binary dir
 set(PROJECT_BINARY_DIR ${CMAKE_BINARY_DIR})

 # Library output directory
 set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

 # Executable output directory
 set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin/)

 # Archive targets output Directory
 set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

 if("${PLATFORM}" STREQUAL "LINUX")
  set(PLATFORM_EXT "LINUX")
  set(EXTERNAL_BUILD FALSE)

  option(STRIP_RELEASE_BINARY "Strip symbols from release binaries" ON)
 elseif("${PLATFORM}" STREQUAL "DARWIN")
  set(ENABLE_LTO        OFF  CACHE BOOL "Enable LTO build?")
  set(ENABLE_ALL_IN_ONE ON   CACHE BOOL "Enable all-in-one build?")
  set(PLATFORM_EXT "DARWIN")
  set(EXTERNAL_BUILD FALSE)

  option(STRIP_RELEASE_BINARY "Strip symbols from release binaries" ON)

 elseif("${PLATFORM}" STREQUAL "EXTERNAL")
  set(PLATFORM_EXT "EXTERNAL")
  set(EXTERNAL_BUILD TRUE)
  set(EXTERNAL_LIBS_INTERFACE "UNDEFINED" CACHE STRING "Path to external libraries' include directory")
  set(EXTERNAL_MEM_HEAP_SIZE_KB "256" CACHE STRING "Size of memory heap, in kilobytes")
 elseif("${PLATFORM}" STREQUAL "OPENWRT")
  set(PLATFORM_EXT "LINUX")
  set(EXTERNAL_BUILD FALSE)

  option(STRIP_RELEASE_BINARY "Strip symbols from release binaries" ON)
 else()
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
 if(DEFINED EXTERNAL_LIBS_INTERFACE AND NOT EXTERNAL_LIBS_INTERFACE STREQUAL "UNDEFINED")
  set(INCLUDE_EXTERNAL_LIBS_INTERFACE )

  foreach(EXTERNAL_LIB_INTERFACE ${EXTERNAL_LIBS_INTERFACE})
   if (NOT EXISTS "${EXTERNAL_LIB_INTERFACE}")
    message(FATAL_ERROR "Interface directory of the external library doesn't exist: ${EXTERNAL_LIB_INTERFACE}")
   endif()

   set(INCLUDE_EXTERNAL_LIBS_INTERFACE ${INCLUDE_EXTERNAL_LIBS_INTERFACE} ${EXTERNAL_LIB_INTERFACE})
  endforeach()
 endif()


# Compiler / Linker flags
 set(COMPILE_FLAGS_JERRY "-fno-builtin")
 if(NOT ("${PLATFORM}" STREQUAL "DARWIN"))
  set(LINKER_FLAGS_COMMON "-Wl,-z,noexecstack")
 endif()
 set(LINKER_FLAGS_COMMON_DARWIN "-lSystem")

 # Turn off linking to compiler's default libc, in case jerry-libc or external is used
 if(NOT USE_LIBC STREQUAL "COMPILER")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -nostdlib")
 endif()

 # LTO
  if(ENABLE_LTO)
   set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} -flto")
   if(NOT ("${PLATFORM}" STREQUAL "DARWIN") AND CMAKE_COMPILER_IS_GNUCC)
    set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} -fno-fat-lto-objects")
   endif()
   set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -flto")
  endif()

 # Turn off stack protector
  set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} -fno-stack-protector")

 # Debug information
  set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} -g -gdwarf-4")

 # Warnings todo: nem kell a macro
  macro(append variable value)
    set(${variable} "${${variable}} ${value}")
  endmacro()

  macro(add_jerry_compile_flags)
    foreach(_flag ${ARGV})
      append(COMPILE_FLAGS_JERRY ${_flag})
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
      set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} ${FLAG}")
    endforeach()
  endif()

 # Static build
  if(NOT ("${PLATFORM}" STREQUAL "DARWIN"))
   set(LINKER_FLAGS_STATIC "-static")
  endif()

 # C
  set(C_FLAGS_JERRY "-std=c99 -pedantic")

# Strip binary
 if(NOT (CMAKE_BUILD_TYPE STREQUAL "Debug") AND ${STRIP_RELEASE_BINARY} STREQUAL "ON")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} -s")
 endif()

# Platform-specific configuration
 set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${LINKER_FLAGS_COMMON_${PLATFORM_EXT}}")
 set(SOURCE_JERRY_STANDALONE_MAIN ${SOURCE_JERRY_STANDALONE_MAIN_${PLATFORM_EXT}})

# User-defined linker-flags
 if (DEFINED USER_DEFINED_LINKER_FLAGS AND NOT ${USER_DEFINED_LINKER_FLAGS} STREQUAL "UNDEFINED")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${USER_DEFINED_LINKER_FLAGS}")
 endif()

# User-defined compile-flags
 if (DEFINED USER_DEFINED_COMPILE_FLAGS AND NOT ${USER_DEFINED_COMPILE_FLAGS} STREQUAL "UNDEFINED")
  set(COMPILE_FLAGS_JERRY "${COMPILE_FLAGS_JERRY} ${USER_DEFINED_COMPILE_FLAGS}")
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