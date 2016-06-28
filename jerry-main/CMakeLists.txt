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

# Platform-specific configuration
 set(MODIFIERS_LISTS ${MODIFIERS_LISTS_${PLATFORM_EXT}})
 set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${LINKER_FLAGS_COMMON_${PLATFORM_EXT}}")

 if(NOT ${EXTERNAL_BUILD})
  add_executable(${JERRY_NAME} ${SOURCE_JERRY_STANDALONE_MAIN_${PLATFORM_EXT}})
 endif()


 # Generage map file
  if("${PLATFORM}" STREQUAL "DARWIN")
   set(MAP_FILE_FLAGS "-Xlinker -map -Xlinker jerry.map")
  else()
   set(MAP_FILE_FLAGS "-Xlinker -Map -Xlinker jerry.map")
  endif()
  set(LINKER_FLAGS_COMMON "${LINKER_FLAGS_COMMON} ${MAP_FILE_FLAGS}")

# Include directories
 # Core interface
  set(INCLUDE_CORE_INTERFACE
      ${CMAKE_SOURCE_DIR}/jerry-core)

 # LIBC interface
 if(USE_JERRY_LIBC)
  set(INCLUDE_LIBC_INTERFACE ${INCLUDE_JERRY_LIBC_INTERFACE})
 endif()

if(NOT ${EXTERNAL_BUILD})

  set_property(TARGET ${JERRY_NAME}
                   PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE} ${C_FLAGS_JERRY}")
  set_property(TARGET ${JERRY_NAME}
               PROPERTY LINK_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE} ${LINKER_FLAGS_COMMON} ${LINKER_FLAGS_STATIC}")
  target_compile_definitions(${JERRY_NAME} PRIVATE ${DEFINES_JERRY})
  target_include_directories(${JERRY_NAME} PRIVATE ${INCLUDE_CORE_INTERFACE})
  target_include_directories(${JERRY_NAME} PRIVATE ${PORT_DIR})
  target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
  target_include_directories(${JERRY_NAME} SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})
  link_directories(${CMAKE_BINARY_DIR})

  set(JERRY_LIBS jerry-core)

  if(BUILD_JERRY_LIBM STREQUAL "ON")
   set(JERRY_LIBS ${JERRY_LIBS} jerry-libm)
  else ()
   set(REQUIRED_LIBS m)
  endif()

  if(USE_JERRY_LIBC)
   set(JERRY_LIBS ${JERRY_LIBS} jerry-libc)
  endif()

  target_link_libraries(${JERRY_NAME} ${JERRY_LIBS} ${REQUIRED_LIBS})

else()
  add_custom_target(${TARGET_NAME} ALL)

  add_custom_command(TARGET ${JERRY_NAME}
                     POST_BUILD
                     COMMAND mkdir -p ${CMAKE_BINARY_DIR}/${JERRY_NAME}
                     COMMAND echo $<TARGET_FILE:${jerry-libm}> > ${CMAKE_BINARY_DIR}/${JERRY_NAME}/list
                     COMMAND echo $<TARGET_FILE:${jerry-core}> >> ${CMAKE_BINARY_DIR}/${JERRY_NAME}/list)

  if(DEFINED EXTERNAL_BUILD_ENTRY_FILE)
   add_library(${JERRY_NAME}-entry STATIC ${EXTERNAL_BUILD_ENTRY_FILE})
   set_property(TARGET ${JERRY_NAME}-entry
                PROPERTY COMPILE_FLAGS "${COMPILE_FLAGS_JERRY} ${FLAGS_COMMON_BUILD_MODE}")
   target_compile_definitions(${JERRY_NAME}-entry PRIVATE ${DEFINES_JERRY})
   target_include_directories(${JERRY_NAME}-entry PRIVATE ${INCLUDE_CORE_INTERFACE})
   target_include_directories(${JERRY_NAME}-entry SYSTEM PRIVATE ${CMAKE_SOURCE_DIR})
   target_include_directories(${JERRY_NAME}-entry SYSTEM PRIVATE ${INCLUDE_LIBC_INTERFACE})
   target_include_directories(${JERRY_NAME}-entry SYSTEM PRIVATE ${INCLUDE_EXTERNAL_LIBS_INTERFACE})
   add_dependencies(${JERRY_NAME} ${JERRY_NAME}-entry)
  endif()

  if(${USE_JERRY_LIBC})
   add_custom_command(TARGET ${JERRY_NAME}
                      POST_BUILD
                      COMMAND echo $<TARGET_FILE:${jerry-libc}> >> ${CMAKE_BINARY_DIR}/${JERRY_NAME}/list)
  endif()

endif()