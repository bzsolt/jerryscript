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

# Architecture-specific compile/link flags
 foreach(FLAG ${FLAGS_COMMON_ARCH})
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${FLAG}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${FLAG}")
 endforeach()

# Remove rdynamic option
 set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS )

# Components
 set(BUILD_JERRY_CORE          ON  CACHE BOOL "Build jerry-core?")
 set(BUILD_JERRY_LIBC          ON  CACHE BOOL "Build jerry-libc?")
 set(BUILD_JERRY_LIBM          ON  CACHE BOOL "Build jerry-libm?")
 set(BUILD_JERRY               ON  CACHE BOOL "Build jerry command line tool?")
 set(BUILD_UNITTESTS           OFF CACHE BOOL "Build unit tests?")

# Optional build settings
 set(ENABLE_JERRY_PORT_DEFAULT ON CACHE BOOL  "Enable jerry-port-default?")
 set(ENABLE_DEBUG              OFF CACHE BOOL "Enable debug build?")
 set(ENABLE_LTO                OFF CACHE BOOL "Enable LTO build?")
 set(ENABLE_ALL_IN_ONE         ON CACHE BOOL "Enable all-in-one build?")


# Setup directories
 # Project binary dir
 set(PROJECT_BINARY_DIR ${CMAKE_BINARY_DIR})

 # Library output directory
 set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

 # Executable output directory
 set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin/)

 # Archive targets output Directory
 set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib/)

 if(BUILD_UNITTESTS STREQUAL "ON")
  set(ENABLE_DEBUG ON)
 endif()

 if(BUILD_JERRY STREQUAL "ON" AND NOT ENABLE_JERRY_PORT_DEFAULT)
  message(FATAL_ERROR "BUILD_JERRY is only supported with ENABLE_JERRY_PORT_DEFAULT")
 endif()

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

  set(EXTERNAL_LIBC_INTERFACE "UNDEFINED" CACHE STRING "Path to external libc include directory")
  set(EXTERNAL_LIBS_INTERFACE "UNDEFINED" CACHE STRING "Path to external libraries' include directory")
  set(EXTERNAL_MEM_HEAP_SIZE_KB "256" CACHE STRING "Size of memory heap, in kilobytes")
 elseif("${PLATFORM}" STREQUAL "OPENWRT")
  set(PLATFORM_EXT "LINUX")
  set(EXTERNAL_BUILD FALSE)

  option(STRIP_RELEASE_BINARY "Strip symbols from release binaries" ON)
 else()
  message(FATAL_ERROR "Platform '${PLATFORM}' is not supported")
 endif()

 if(CMAKE_COMPILER_IS_GNUCC)
  if(ENABLE_LTO)
   # Use gcc-ar and gcc-ranlib to support LTO
   set (CMAKE_AR "gcc-ar")
   set(CMAKE_RANLIB "gcc-ranlib")
  endif()
 endif()

# Should we use external libc?
 if(DEFINED COMPILER_DEFAULT_LIBC AND COMPILER_DEFAULT_LIBC STREQUAL "ON")
  if(DEFINED EXTERNAL_LIBC_INTERFACE AND NOT EXTERNAL_LIBC_INTERFACE STREQUAL "UNDEFINED")
    message(FATAL_ERROR "EXTERNAL_LIBC_INTERFACE='${EXTERNAL_LIBC_INTERFACE}' should not be set in case compiler's default libc is used (COMPILER_DEFAULT_LIBC=ON)")
  endif()
  set(USE_JERRY_LIBC FALSE)
  set(USE_EXTERNAL_LIBC FALSE)
 elseif(NOT DEFINED EXTERNAL_LIBC_INTERFACE OR EXTERNAL_LIBC_INTERFACE STREQUAL "UNDEFINED")
  set(USE_JERRY_LIBC TRUE)
  if(BUILD_JERRY_LIBC STREQUAL "OFF")
   find_library(JERRY_LIBC_FOUND NAMES jerry-libc PATHS CMAKE_ARCHIVE_OUTPUT_DIRECTORY)
   if(NOT JERRY_LIBC_FOUND)
    set(USE_JERRY_LIBC FALSE)
   endif()
  endif()

  set(USE_EXTERNAL_LIBC FALSE)
 else()
  set(USE_JERRY_LIBC FALSE)

  if(NOT EXISTS "${EXTERNAL_LIBC_INTERFACE}/stdlib.h")
   message(FATAL_ERROR "It seems that external libc interface '${EXTERNAL_LIBC_INTERFACE}' doesn't provide stdlib.h header")
   set(USE_EXTERNAL_LIBC FALSE)
  endif()

  set(INCLUDE_LIBC_INTERFACE ${EXTERNAL_LIBC_INTERFACE})
  set(USE_EXTERNAL_LIBC TRUE)
 endif()

 # should we use default or external port?
 if (ENABLE_JERRY_PORT_DEFAULT STREQUAL "ON")
  set(PORT_DIR ${CMAKE_SOURCE_DIR}/targets/default)
  if (COMPILER_DEFAULT_LIBC STREQUAL "ON" OR NOT (USE_JERRY_LIBC OR USE_EXTERNAL_LIBC))
   set(DEFINES_JERRY ${DEFINES_JERRY} _BSD_SOURCE)
  endif()
 elseif(DEFINED EXTERNAL_PORT_DIR AND NOT EXTERNAL_PORT_DIR STREQUAL "UNDEFINED")
   set(PORT_DIR ${EXTERNAL_PORT_DIR})
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

 # Turn off linking to compiler's default libc, in case jerry-libc is used
 if(USE_JERRY_LIBC OR USE_EXTERNAL_LIBC)
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

 # Warnings
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
    if(USE_JERRY_LIBC)
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

 # build mode specific compile/link flags
 if(ENABLE_DEBUG)
  if(BUILD_UNITTESTS STREQUAL "ON")
   set(FLAGS_COMMON_BUILD_MODE "-O3")
  endif()
 else()
  set(FLAGS_COMMON_BUILD_MODE "-Os")
 endif()

# Strip binary
 if(NOT ENABLE_DEBUG AND ${STRIP_RELEASE_BINARY} STREQUAL "ON")
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

# External
if(${EXTERNAL_BUILD})
  set(TARGET_NAME external)
  add_custom_target(${TARGET_NAME} ALL)

  add_custom_command(TARGET ${TARGET_NAME}
                     POST_BUILD
                     COMMAND mkdir -p ${CMAKE_BINARY_DIR}/${TARGET_NAME}
                     COMMAND echo $<TARGET_FILE:jerry-libm> > ${CMAKE_BINARY_DIR}/${TARGET_NAME}/list
                     COMMAND echo $<TARGET_FILE:jerry-core> >> ${CMAKE_BINARY_DIR}/${TARGET_NAME}/list)

  if(DEFINED EXTERNAL_BUILD_ENTRY_FILE)
   add_library(${TARGET_NAME}-entry STATIC ${EXTERNAL_BUILD_ENTRY_FILE})
   set_property(TARGET ${TARGET_NAME}-entry
                PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE}}")
   target_compile_definitions(${TARGET_NAME}-entry PRIVATE ${DEFINES_JERRY})
   target_include_directories(${TARGET_NAME}-entry PRIVATE ${INCLUDE_CORE_INTERFACE})
   target_include_directories(${TARGET_NAME}-entry SYSTEM PRIVATE ${CMAKE_SOURCE_DIR})
   target_include_directories(${TARGET_NAME}-entry SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
   target_include_directories(${TARGET_NAME}-entry SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})
   add_dependencies(${TARGET_NAME} ${TARGET_NAME}-entry)
  endif()

  if(${USE_JERRY_LIBC})
   add_custom_command(TARGET ${TARGET_NAME}
                      POST_BUILD
                      COMMAND echo $<TARGET_FILE:jerry-libc> >> ${CMAKE_BINARY_DIR}/${TARGET_NAME}/list)
  endif()

endif()
