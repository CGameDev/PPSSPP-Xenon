// SPDX-License-Identifier: GPL-2.0-or-later
// Host tests force the same endian wrapper used on Xenon.
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
typedef signed char s8; typedef unsigned char u8;
typedef short s16; typedef unsigned short u16;
typedef int s32; typedef unsigned int u32;
#if defined(_MSC_VER)
typedef __int64 s64; typedef unsigned __int64 u64;
#else
typedef long long s64; typedef unsigned long long u64;
#endif
static u16 bswap16(u16 x) { return (u16)((x >> 8) | (x << 8)); }
static u32 bswap32(u32 x) { return (x >> 24) | ((x >> 8) & 0xff00U) | ((x << 8) & 0xff0000U) | (x << 24); }
static u64 bswap64(u64 x) { return ((u64)bswap32((u32)x) << 32) | bswap32((u32)(x >> 32)); }
static float bswapf(float value) {
    u32 bits; std::memcpy(&bits,&value,sizeof(bits)); bits=bswap32(bits);
    std::memcpy(&value,&bits,sizeof(bits)); return value;
}
static double bswapd(double value) {
    u64 bits; std::memcpy(&bits,&value,sizeof(bits)); bits=bswap64(bits);
    std::memcpy(&value,&bits,sizeof(bits)); return value;
}
#define COMMON_BIG_ENDIAN 1
#define COMMON_LITTLE_ENDIAN 0
#include "Common/Swap.h"
struct State { u32 reversenormals; } gstate;
struct Cache { float morphWeights[8]; } gstate_c;
class VertexDecoderDX9 {
public:
    unsigned char *decoded_; const unsigned char *ptr_;
    int morphcount, onesize_, nrmoff;
    struct Format { int nrmoff; } decFmt;
    void Step_NormalS16Morph() const;
};
#include "morph_function.inc"
#include "unsigned_predicates.inc"
#include "prefix_flag.inc"
typedef unsigned int DWORD;
typedef void VOID;
struct D3DPOINT { int x, y; };
struct Rect { int x1, y1, x2, y2; };
struct XboxTilingSetting { int tileCount; Rect tilingRects[15]; };
#include "tile_function.inc"
static void testRoot() {
    std::string currentDir_;
#include "root_initialization.inc"
    assert(currentDir_ == "game:\\");
}
int main() {
    assert(sizeof(s16) == 2 && sizeof(u32) == 4);
    assert(bswap64(1) == ((u64)1 << 56));
    assert(bswapf(bswapf(1.0f)) == 1.0f && bswapd(bswapd(1.0)) == 1.0);
    const float weights[] = {0.0f, 0.25f, 0.5f, 1.0f, -1.0f, 1.5f};
    s16_le input[6]; float output[3];
    VertexDecoderDX9 decoder;
    decoder.decoded_ = (unsigned char *)output;
    decoder.ptr_ = (const unsigned char *)input;
    decoder.nrmoff = decoder.decFmt.nrmoff = 0;
    decoder.onesize_ = 3 * sizeof(s16_le); decoder.morphcount = 1;
#ifdef EXPECT_LEGACY_MORPH
    input[0] = 16384; input[1] = input[2] = 0;
    gstate.reversenormals = 0; gstate_c.morphWeights[0] = 1.0f;
    decoder.Step_NormalS16Morph();
    assert(output[0] == 0.0f);
    std::puts("PASS negative control: original wrapped multiply truncates fractional normal to zero");
    return 0;
#endif
    unsigned cases = 0;
    for (int sample = -32768; sample <= 32767; ++sample) {
        input[0] = (s16)sample; input[1] = (s16)-12345; input[2] = (s16)32767;
        for (unsigned w = 0; w < sizeof(weights)/sizeof(weights[0]); ++w) {
            for (unsigned reverse = 0; reverse <= 1; ++reverse) {
                gstate.reversenormals = reverse; gstate_c.morphWeights[0] = weights[w];
                decoder.Step_NormalS16Morph();
                float scale = (reverse ? -weights[w] : weights[w]) * (1.0f/32767.0f);
                const int expectedInputs[] = {sample, -12345, 32767};
                for (int j = 0; j < 3; ++j)
                    assert(std::fabs(output[j] - (float)expectedInputs[j]*scale) < 0.000001f);
                ++cases;
            }
        }
    }
    decoder.morphcount = 2;
    input[0] = 16384; input[1] = -32768; input[2] = 1;
    input[3] = -8192; input[4] = 32767; input[5] = -1;
    gstate.reversenormals = 0;
    gstate_c.morphWeights[0] = 0.25f; gstate_c.morphWeights[1] = 0.75f;
    decoder.Step_NormalS16Morph();
    assert(std::fabs(output[0] - (-2048.0f/32767.0f)) < 0.000001f);
    assert(std::fabs(output[1] - ((-32768.0f*.25f+32767.0f*.75f)/32767.0f)) < 0.000001f);
    const u32 values[] = {0U,1U,5U,99U,100U,8191U,8192U,8193U,0x7fffffffU,0x80000000U,0xffffffffU};
    for (unsigned i = 0; i < sizeof(values)/sizeof(values[0]); ++i) {
        u32_le v(values[i]);
        assert(moduleArgs(v) == (values[i] > 0U));
        assert(startPriority(v) == (values[i] > 0U));
        assert(startStack(v) == (values[i] > 0U));
        assert(optionStack(v) == (values[i] > 0U));
        assert(atracEnd(v) == (values[i] > 0U));
        assert(secureEntries(v) == (values[i] > 99U));
        assert(normalEntries(v) == (values[i] > 8192U));
        assert(systemEntries(v) == (values[i] > 5U));
    }
    for (u32 prefix = 0; prefix < (1U << 20); ++prefix)
        for (int i = 0; i < 4; ++i)
            assert(negateFlag(prefix,i) == (((prefix >> (16+i)) & 1U) != 0));
    XboxTilingSetting tiles = {}; D3DPOINT point;
    LargestTileRectSize(tiles, &point); assert(point.x == 0 && point.y == 0);
    tiles.tileCount = 2;
    tiles.tilingRects[0].x2 = 100; tiles.tilingRects[0].y2 = 30;
    tiles.tilingRects[1].x2 = 80; tiles.tilingRects[1].y2 = 50;
    LargestTileRectSize(tiles, &point); assert(point.x == 100 && point.y == 50);
    testRoot();
    std::printf("PASS: %u morph cases, blended normals, unsigned limits, tile bounds and initial root\n", cases);
    return 0;
}
