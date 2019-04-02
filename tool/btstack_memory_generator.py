#!/usr/bin/env python

import os
import sys

copyright = """/*
 * Copyright (C) 2014 BlueKitchen GmbH
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holders nor the names of
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 * 4. Any redistribution, use, or modification is done solely for
 *    personal benefit and not for any commercial purpose or for
 *    monetary gain.
 *
 * THIS SOFTWARE IS PROVIDED BY BLUEKITCHEN GMBH AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MATTHIAS
 * RINGWALD OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
 * THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * Please inquire about commercial licensing options at 
 * contact@bluekitchen-gmbh.com
 *
 */
"""

hfile_header_begin = """

/*
 *  btstack_memory.h
 *
 *  @brief BTstack memory management via configurable memory pools
 *
 */

#ifndef __BTSTACK_MEMORY_H
#define __BTSTACK_MEMORY_H

#if defined __cplusplus
extern "C" {
#endif

#include "btstack_config.h"
    
// Core
#include "hci.h"
#include "l2cap.h"

// Classic
#include "classic/avdtp_sink.h"
#include "classic/avdtp_source.h"
#include "classic/avrcp.h"
#include "classic/bnep.h"
#include "classic/btstack_link_key_db.h"
#include "classic/btstack_link_key_db_memory.h"
#include "classic/goep_server.h"
#include "classic/hfp.h"
#include "classic/rfcomm.h"
#include "classic/sdp_server.h"

// BLE
#ifdef ENABLE_BLE
#include "ble/gatt_client.h"
#include "ble/sm.h"
#endif

/* API_START */

/**
 * @brief Initializes BTstack memory pools.
 */
void btstack_memory_init(void);

/* API_END */
"""

hfile_header_end = """
#if defined __cplusplus
}
#endif

#endif // __BTSTACK_MEMORY_H
"""

cfile_header_begin = """
/*
 *  btstack_memory.h
 *
 *  @brief BTstack memory management via configurable memory pools
 *
 *  @note code generated by tool/btstack_memory_generator.py
 *  @note returnes buffers are initialized with 0
 *
 */

#include "btstack_memory.h"
#include "btstack_memory_pool.h"

#include <stdlib.h>

"""

header_template = """STRUCT_NAME_t * btstack_memory_STRUCT_NAME_get(void);
void   btstack_memory_STRUCT_NAME_free(STRUCT_NAME_t *STRUCT_NAME);"""

code_template = """
// MARK: STRUCT_TYPE
#if !defined(HAVE_MALLOC) && !defined(POOL_COUNT)
    #if defined(POOL_COUNT_OLD_NO)
        #error "Deprecated POOL_COUNT_OLD_NO defined instead of POOL_COUNT. Please update your btstack_config.h to use POOL_COUNT."
    #else
        #define POOL_COUNT 0
    #endif
#endif

#ifdef POOL_COUNT
#if POOL_COUNT > 0
static STRUCT_TYPE STRUCT_NAME_storage[POOL_COUNT];
static btstack_memory_pool_t STRUCT_NAME_pool;
STRUCT_NAME_t * btstack_memory_STRUCT_NAME_get(void){
    void * buffer = btstack_memory_pool_get(&STRUCT_NAME_pool);
    if (buffer){
        memset(buffer, 0, sizeof(STRUCT_TYPE));
    }
    return (STRUCT_NAME_t *) buffer;
}
void btstack_memory_STRUCT_NAME_free(STRUCT_NAME_t *STRUCT_NAME){
    btstack_memory_pool_free(&STRUCT_NAME_pool, STRUCT_NAME);
}
#else
STRUCT_NAME_t * btstack_memory_STRUCT_NAME_get(void){
    return NULL;
}
void btstack_memory_STRUCT_NAME_free(STRUCT_NAME_t *STRUCT_NAME){
    // silence compiler warning about unused parameter in a portable way
    (void) STRUCT_NAME;
};
#endif
#elif defined(HAVE_MALLOC)
STRUCT_NAME_t * btstack_memory_STRUCT_NAME_get(void){
    void * buffer = malloc(sizeof(STRUCT_TYPE));
    if (buffer){
        memset(buffer, 0, sizeof(STRUCT_TYPE));
    }
    return (STRUCT_NAME_t *) buffer;
}
void btstack_memory_STRUCT_NAME_free(STRUCT_NAME_t *STRUCT_NAME){
    free(STRUCT_NAME);
}
#endif
"""

init_template = """#if POOL_COUNT > 0
    btstack_memory_pool_create(&STRUCT_NAME_pool, STRUCT_NAME_storage, POOL_COUNT, sizeof(STRUCT_TYPE));
#endif"""

def writeln(f, data):
    f.write(data + "\n")

def replacePlaceholder(template, struct_name):
    struct_type = struct_name + '_t'
    if struct_name.endswith('try'):
        pool_count = "MAX_NR_" + struct_name.upper()[:-3] + "TRIES"
    else:
        pool_count = "MAX_NR_" + struct_name.upper() + "S"
    pool_count_old_no = pool_count.replace("MAX_NR_", "MAX_NO_")
    snippet = template.replace("STRUCT_TYPE", struct_type).replace("STRUCT_NAME", struct_name).replace("POOL_COUNT_OLD_NO", pool_count_old_no).replace("POOL_COUNT", pool_count)
    return snippet
    
list_of_structs = [
    ["hci_connection"],
    ["l2cap_service", "l2cap_channel"],
    ["rfcomm_multiplexer", "rfcomm_service", "rfcomm_channel"],
    ["btstack_link_key_db_memory_entry"],
    ["bnep_service", "bnep_channel"],
    ["hfp_connection"],
    ["service_record_item"],
    ["avdtp_stream_endpoint"],
    ["avdtp_connection"],
    ["avrcp_connection"],
    ["avrcp_browsing_connection"],
    ["goep_server_service"], ["goep_server_connection"] 
]

list_of_le_structs = [["gatt_client", "whitelist_entry", "sm_lookup_entry"]]

"""
"""

btstack_root = os.path.abspath(os.path.dirname(sys.argv[0]) + '/..')
file_name = btstack_root + "/src/btstack_memory"
print ('Generating %s.[h|c]' % file_name)

f = open(file_name+".h", "w")
writeln(f, copyright)
writeln(f, hfile_header_begin)
for struct_names in list_of_structs:
    writeln(f, "// "+ ", ".join(struct_names))
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(header_template, struct_name))
    writeln(f, "")
writeln(f, "#ifdef ENABLE_BLE")
for struct_names in list_of_le_structs:
    writeln(f, "// "+ ", ".join(struct_names))
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(header_template, struct_name))
writeln(f, "#endif")
writeln(f, hfile_header_end)
f.close();


f = open(file_name+".c", "w")
writeln(f, copyright)
writeln(f, cfile_header_begin)
for struct_names in list_of_structs:
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(code_template, struct_name))
    writeln(f, "")
writeln(f, "#ifdef ENABLE_BLE")
for struct_names in list_of_le_structs:
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(code_template, struct_name))
    writeln(f, "")
writeln(f, "#endif")


writeln(f, "// init")
writeln(f, "void btstack_memory_init(void){")
for struct_names in list_of_structs:
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(init_template, struct_name))
writeln(f, "#ifdef ENABLE_BLE")
for struct_names in list_of_le_structs:
    for struct_name in struct_names:
        writeln(f, replacePlaceholder(init_template, struct_name))
writeln(f, "#endif")
writeln(f, "}")
f.close();
    
