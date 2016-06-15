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

cmake_minimum_required (VERSION 2.8.12)
project (Jerry C)

set(JERRY_NAME    jerry)

# Sources
 # Platform-specific
  # Jerry standalone
   # Linux
    set(SOURCE_JERRY_STANDALONE_MAIN_LINUX main-unix.c)

   # Darwin
    set(SOURCE_JERRY_STANDALONE_MAIN_DARWIN main-unix.c)

   # MCU
    # stm32f3
     set(SOURCE_JERRY_STANDALONE_MAIN_MCU_STM32F3 main-mcu.c)

    # stm32f4
     set(SOURCE_JERRY_STANDALONE_MAIN_MCU_STM32F4 main-mcu.c)

# Platform-specific configuration
 set(MODIFIERS_LISTS ${MODIFIERS_LISTS_${PLATFORM_EXT}})
 set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${LINKER_FLAGS_COMMON_${PLATFORM_EXT}}")

 if(NOT ${EXTERNAL_BUILD})
  add_executable(${JERRY_NAME} ${SOURCE_JERRY_STANDALONE_MAIN_${PLATFORM_EXT}})
 endif()

# Include directories
 # Core interface
  set(INCLUDE_CORE_INTERFACE
      ${CMAKE_SOURCE_DIR}/jerry-core)

set_property(TARGET ${JERRY_NAME}
                 PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE} ${C_FLAGS_JERRY}")
set_property(TARGET ${JERRY_NAME}
             PROPERTY LINK_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE} ${LINKER_FLAGS_COMMON} ${LINKER_FLAGS_STATIC}")
target_compile_definitions(${JERRY_NAME} PRIVATE ${DEFINES_JERRY})
target_include_directories(${JERRY_NAME} PRIVATE ${INCLUDE_CORE_INTERFACE})
target_include_directories(${JERRY_NAME} PRIVATE ${PORT_DIR})
target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})

target_link_libraries(${JERRY_NAME} ${JERRY_LIBC_NAME} ${JERRY_CORE_NAME} ${JERRY_LIBM_NAME} ${PREFIX_IMPORTED_LIB}libgcc)
