/* Copyright 2016 University of Szeged.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef JERRY_DEBUGGER_H
#define JERRY_DEBUGGER_H

#include "debugger-types.h"

extern void remote_init(void);
extern void connection_closed(void);
extern void send_to_client(uint8_t* data);

/**
 * Package types.
 */
typedef enum
{
  JERRY_DEBUG_HEADER_INFO,                /**< header package */
  JERRY_DEBUG_LINE_INFO,                  /**< line package */
  JERRY_DEBUG_MAP_INFO,                   /**< literal, index package */
} debug_package_type_t;

/**
 * Debugger command types.
 */
typedef enum name
{
  GET,                                    /**< get request */
  CONT,                                   /**< continue request */
} debug_command_type_t;

/**
 * Package header struct.
 */
typedef struct
{
  uint16_t size;                          /**< package size */
  uint8_t type;                           /**< package type */
} debug_package_header_t;

/**
 * Literal map struct.
 */
typedef struct
{
  debug_package_header_t header;          /**< package header */
  uint8_t literal_len;                   /**< literal length */
  uint8_t literal[255];                   /**< literal name */
  uint16_t index;                         /**< literal index */
} debug_literal_map_t;

/**
 * Offset line pair struct.
 */
typedef struct
{
  void* offset;                           /**< bytecode offset */
  uint32_t line;                          /**< bytecode line */
} debug_offset_line_pair_t;

/**
 * Package header info struct.
 */
typedef struct
{
  debug_package_header_t header;          /**< package header */
  void* start_address_p;                  /**< byte start offset */
  uint8_t name_len;                       /**< filename length, max 255 character */
  uint8_t name[255];                      /**< filenames */
} debug_header_info_t;

/**
 * Package line info struct.
 */
typedef struct
{
  debug_package_header_t header;          /**< package header */
  uint8_t count;                          /**< line count */
  debug_offset_line_pair_t pairs[255];    /**< if package > 255 --> take to pieces */
} debug_line_info_t;

#endif /* JERRY_DEBUG_H */
