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
set(JERRY_LIBC_NAME    jerry-libc)

project (${JERRY_LIBC_NAME} C)

# Compiler / linker flags
set(COMPILE_FLAGS_LIBC "${COMPILE_FLAGS_JERRY} ${C_FLAGS_JERRY}")

# Definitions
  set(DEFINES_LIBC )

  if(ENABLE_DEBUG)
   set(DEFINES_LIBC_BUILD_MODE DEBUG)
  else()
   set(DEFINES_LIBC_BUILD_MODE NDEBUG)
  endif()

# Architecture-specific
  # x86_64
   set(DEFINES_LIBC_X86_64 __TARGET_HOST_x64)
  # ARMv7-hf
   set(DEFINES_LIBC_ARMV7_HF __TARGET_HOST_ARMv7 __TARGET_HOST_ARMv7_HARD_FLOAT)
  # ARMv7-el
   set(DEFINES_LIBC_ARMV7_EL __TARGET_HOST_ARMv7 __TARGET_HOST_ARMv7_SOFT_FLOAT)
  # x86
   set(DEFINES_LIBC_X86 __TARGET_HOST_x86)

 # Platform-specific
  # Linux
   set(DEFINES_LIBC_LINUX __TARGET_HOST)
  # Darwin
   set(DEFINES_LIBC_DARWIN __TARGET_HOST)


# Include directories
 set(INCLUDE_LIBC ${CMAKE_CURRENT_SOURCE_DIR})

# Sources
 file(GLOB SOURCE_LIBC *.c)

 # Platform-specific
  # Linux
  if(DEFINED PLATFORM AND ((PLATFORM STREQUAL "LINUX") OR (PLATFORM STREQUAL "DARWIN")))
   file(GLOB TARGET_SPECIFIC_LIBC_SOURCE target/posix/*.c target/posix/*.S)
  endif()

# Architecture-specific configuration
 if(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86_64")
  set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_X86_64})
 elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "armv7l-hf")
  set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_ARMV7_HF})
 elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "armv7l-el")
  set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_ARMV7_EL})
 elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "i686")
  set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_X86})
 else()
  message(FATAL_ERROR "Unsupported machine architecture")
 endif()

# Platform-specific configuration
 set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_${PLATFORM}})
 set(DEFINES_LIBC ${DEFINES_LIBC} ${DEFINES_LIBC_BUILD_MODE})
 set(INCLUDE_LIBC ${INCLUDE_LIBC} ${INCLUDE_LIBC_${PLATFORM_EXT}})

 add_library(${JERRY_LIBC_NAME} STATIC ${SOURCE_LIBC} ${TARGET_SPECIFIC_LIBC_SOURCE})
 set_property(TARGET ${JERRY_LIBC_NAME} PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_LIBC} ${FLAGS_COMMON_BUILD_MODE}")

 target_compile_definitions(${JERRY_LIBC_NAME} PRIVATE ${DEFINES_LIBC})
 target_include_directories(${JERRY_LIBC_NAME} PRIVATE ${INCLUDE_LIBC})
 target_include_directories(${JERRY_LIBC_NAME} SYSTEM PRIVATE ${CMAKE_SOURCE_DIR}/jerry-libc/include)
