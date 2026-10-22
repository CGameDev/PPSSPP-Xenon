// SPDX-License-Identifier: GPL-2.0-or-later
#include <cassert>
#include <cstdio>
#include "xxhash.c"
int main() {
    unsigned char bytes[4096];
    for (unsigned i = 0; i < sizeof(bytes); ++i) bytes[i] = (unsigned char)(i*37U+11U);
    const int lengths[] = {0,1,3,15,16,17,255,4096};
    const unsigned seeds[] = {0,1,0x12345678U,0xffffffffU};
    for (unsigned s=0; s<sizeof(seeds)/sizeof(seeds[0]); ++s) {
        for (unsigned n=0; n<sizeof(lengths)/sizeof(lengths[0]); ++n) {
            unsigned hash = XXH32(bytes,lengths[n],seeds[s]);
            void *state = XXH32_init(seeds[s]); assert(state);
            for (int i=0; i<lengths[n];) {
                int chunk = lengths[n]-i < 7 ? lengths[n]-i : 7;
                assert(XXH32_update(state,bytes+i,chunk)==XXH_OK); i+=chunk;
            }
            assert(XXH32_digest(state)==hash);
            std::printf("%08x\n",hash);
        }
    }
    return 0;
}
