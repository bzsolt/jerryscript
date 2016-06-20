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
project (Unittest C)

# Include directories
 # Core interface
  set(INCLUDE_CORE_INTERFACE
      ${CMAKE_SOURCE_DIR}/jerry-core)

 # Unit tests main modules
   file(GLOB SOURCE_UNIT_TEST_MAIN_MODULES *.c)

# Unit tests declaration
  if(("${PLATFORM}" STREQUAL "LINUX") OR ("${PLATFORM}" STREQUAL "DARWIN"))
   add_custom_target(unittests)

   foreach(SOURCE_UNIT_TEST_MAIN ${SOURCE_UNIT_TEST_MAIN_MODULES})
    get_filename_component(TARGET_NAME ${SOURCE_UNIT_TEST_MAIN} NAME_WE)
    set(TARGET_NAME unit-${TARGET_NAME})

    add_executable(${TARGET_NAME} ${SOURCE_UNIT_TEST_MAIN})
    set_property(TARGET ${TARGET_NAME}
                 PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_JERRY} ${C_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE}")
    set_property(TARGET ${TARGET_NAME}
                PROPERTY LINK_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE} ${LINKER_FLAGS_COMMON}")
    target_include_directories(${TARGET_NAME} PRIVATE ${INCLUDE_CORE_INTERFACE})
    target_include_directories(${TARGET_NAME} SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})

    link_directories(${CMAKE_BINARY_DIR})

    if(("${PLATFORM}" STREQUAL "DARWIN") AND (NOT (CMAKE_COMPILER_IS_GNUCC)))
      target_link_libraries(${TARGET_NAME} ${JERRY_CORE_NAME} ${JERRY_LIBC_NAME} jerry-libm ${PREFIX_IMPORTED_LIB}libclang_rt.osx)
    else()
      target_link_libraries(${TARGET_NAME} ${JERRY_CORE_NAME} ${JERRY_LIBC_NAME} jerry-libm ${PREFIX_IMPORTED_LIB}libgcc)
    endif()

    add_dependencies(unittests ${TARGET_NAME})
   endforeach()
  endif()