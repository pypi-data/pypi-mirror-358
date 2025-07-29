#include <stdio.h>
#include "stc/cstr.h"

// hmap of cstr => long*
#define i_type Ptrmap
#define i_keypro cstr
#define i_val long*
#define i_valraw long
#define i_valfrom(raw) c_new(long, raw)
#define i_valtoraw(x) **x
#define i_valclone(x) c_new(long, *x)
#define i_valdrop(x) free(*x)
#include "stc/hmap.h"

int main(void)
{
    Ptrmap map = {0};

    puts("Map cstr => long*:");
    Ptrmap_insert(&map, cstr_lit("Test1"), c_new(long, 1));
    Ptrmap_insert(&map, cstr_lit("Test2"), c_new(long, 2));

    // Simple: emplace() implicitly creates cstr from const char* and an owned long* from long!
    Ptrmap_emplace(&map, "Test3", 3);
    Ptrmap_emplace(&map, "Test4", 4);

    for (c_each_kv(name, number, Ptrmap, map))
        printf("%s: %ld\n", cstr_str(name), **number);
    puts("");

    Ptrmap_drop(&map);
}
