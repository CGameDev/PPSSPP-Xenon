// SPDX-License-Identifier: GPL-2.0-or-later
// Host failure injection around the actual patched launcher functions.
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
#define SUCCEEDED(hr) ((hr) >= 0)
#define D3DFMT(x) (x)
enum { D3DFMT_A8R8G8B8, D3DPOOL_MANAGED };
struct D3DLOCKED_RECT { void *pBits; int Pitch; };
static int scenario, allocations, frees, creates, locks, unlocks, releases, decodes;
static uint32_t pixels[6]; // Two pixels per row, with a padding sentinel.
struct IDirect3DTexture9 {
    int LockRect(int, D3DLOCKED_RECT *r, void *, int) {
        ++locks;
        if (scenario == 5) return -1;
        r->pBits = pixels; r->Pitch = 3 * sizeof(uint32_t); return 0;
    }
    void UnlockRect(int) { ++unlocks; }
    void Release() { ++releases; }
};
static IDirect3DTexture9 texture;
struct Device {
    int CreateTexture(int, int, int, int, int, int, IDirect3DTexture9 **out, void *) {
        ++creates;
        if (scenario == 4) return -1;
        *out = &texture; return 0;
    }
};
static Device device;
static Device *pD3Ddevice = &device;
static bool ISO_ReadIcon(const char *, std::vector<uint8_t> &data) {
    if (scenario == 0) return false;
    if (scenario != 1) data.push_back(1);
    return true;
}
static int decode(int *w, int *h, unsigned char **rgba) {
    ++decodes;
    if (scenario == 2) return 0;
    *rgba = (unsigned char *)std::malloc(16); ++allocations;
    for (int i = 0; i < 16; ++i) (*rgba)[i] = (unsigned char)(i + 1);
    *w = scenario == 3 ? 0 : 2; *h = 2; return 1;
}
static int pngLoadPtr(const unsigned char *, size_t, int *w, int *h, unsigned char **p, bool) {
    return decode(w, h, p);
}
static int pngLoad(const char *, int *w, int *h, unsigned char **p, bool) {
    return decode(w, h, p);
}
static void trackedFree(void *p) { if (p) ++frees; std::free(p); }
class XboxLauncher {
public:
    IDirect3DTexture9 *LoadGameIcon(const std::string &);
    IDirect3DTexture9 *LoadPNGTexture(const char *);
};
#define free trackedFree
#include "launcher_texture_functions.inc"
#undef free

int main() {
    XboxLauncher launcher;
    int cases = 0;
    for (int loader = 0; loader < 2; ++loader) {
        for (scenario = loader ? 2 : 0; scenario <= 6; ++scenario) {
            allocations = frees = creates = locks = unlocks = releases = decodes = 0;
            for (int i = 0; i < 6; ++i) pixels[i] = 0xDEADBEEF;
            IDirect3DTexture9 *result = loader ? launcher.LoadPNGTexture("fixture.png")
                : launcher.LoadGameIcon("fixture.iso");
            assert(allocations == frees);
            if (scenario <= 1) assert(decodes == 0);
            if (scenario <= 3) assert(creates == 0 && locks == 0);
            if (scenario == 4) assert(creates == 1 && locks == 0 && releases == 0);
            if (scenario == 5) assert(locks == 1 && releases == 1 && unlocks == 0);
            if (scenario == 6) {
                assert(result == &texture && locks == 1 && unlocks == 1 && releases == 0);
                assert(pixels[0] == 0x04010203 && pixels[1] == 0x08050607);
                assert(pixels[3] == 0x0C090A0B && pixels[4] == 0x100D0E0F);
                assert(pixels[2] == 0xDEADBEEF && pixels[5] == 0xDEADBEEF);
            } else assert(result == NULL && unlocks == 0);
            ++cases;
        }
    }
    assert(cases == 12);
    return 0;
}
