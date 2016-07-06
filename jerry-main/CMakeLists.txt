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

if(NOT ${USE_PORT_DIR} STREQUAL "DEFAULT")
 message(FATAL_ERROR "JERRY_NAME is not supported with PORT_DIR: ${PORT_DIR}")
endif()

# Sources
  # Jerry standalone
  set(SOURCE_JERRY_STANDALONE_MAIN main-unix.c)

 # Generage map file
  if("${PLATFORM}" STREQUAL "DARWIN")
   set(MAP_FILE_FLAGS "-Xlinker -map")
  else()
   set(MAP_FILE_FLAGS "-Xlinker -Map")
  endif()
  set(MAP_FILE_FLAGS "${MAP_FILE_FLAGS} -Xlinker jerry.map")
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${MAP_FILE_FLAGS}")

# Include directories
 # Core interface
  set(INCLUDE_CORE_INTERFACE ${CMAKE_SOURCE_DIR}/jerry-core)

  add_executable(${JERRY_NAME} ${SOURCE_JERRY_STANDALONE_MAIN})
  set_property(TARGET ${JERRY_NAME}
                   PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_COMMON} ${C_FLAGS_COMMON}")
  set_property(TARGET ${JERRY_NAME}
               PROPERTY LINK_FLAGS "${COMPILE_FLAGS_COMMON} ${LINKER_FLAGS_STATIC} ${LINKER_FLAGS_COMMON}")
  target_compile_definitions(${JERRY_NAME} PRIVATE ${DEFINES_JERRY})
  target_include_directories(${JERRY_NAME} PRIVATE ${PORT_DIR})
  target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
  target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})
  link_directories(${CMAKE_BINARY_DIR})

  set(JERRY_LIBS jerry-core)

  if(BUILD_JERRY_LIBM STREQUAL "ON")
   set(JERRY_LIBS ${JERRY_LIBS} jerry-libm)
  endif()

  if(${USE_LIBC} STREQUAL "JERRY")
   set(JERRY_LIBS ${JERRY_LIBS} jerry-libc)
  endif()

  target_link_libraries(${JERRY_NAME} ${JERRY_LIBS})
