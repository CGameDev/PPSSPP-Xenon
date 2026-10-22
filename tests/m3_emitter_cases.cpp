// SPDX-License-Identifier: GPL-2.0-or-later
// Execute the emitter as a host word generator, never the generated PPC code.
#include <cassert>
#include <cstdio>
#include <vector>
typedef unsigned int u32; typedef int s32; typedef short s16;
typedef int PPCReg;
enum { R1=1, R5=5, R10=10, R12=12 };
class PPCXEmitter {
public:
    std::vector<u32> words;
    void Write32(u32 word) { words.push_back(word); }
    void MFLR(PPCReg); void MTLR(PPCReg);
    void LI(PPCReg, unsigned short); void LIS(PPCReg, unsigned short);
    void ORI(PPCReg, PPCReg, unsigned short);
    void MOVI2R(PPCReg, unsigned int);
    void ADDI(PPCReg, PPCReg, short);
    void STW(PPCReg, PPCReg, int); void STWU(PPCReg, PPCReg, int);
    void LD(PPCReg, PPCReg, int); void STD(PPCReg, PPCReg, int);
    void LWZ(PPCReg, PPCReg, int);
    void LFD(PPCReg, PPCReg, unsigned short); void SFD(PPCReg, PPCReg, unsigned short);
    void Prologue(); void Epilogue();
};
#include "emitter_functions.inc"
int main() {
    PPCXEmitter emitter; emitter.Prologue(); emitter.Epilogue();
    assert(emitter.words.size() == 82);
    for (int i = 0; i < 18; ++i) {
        assert((emitter.words[1+i] & 0xffffU) == ((u32)(-(19-i)*8) & 0xffffU));
        assert((emitter.words[42+i] & 0xffffU) == ((u32)(-(19-i)*8) & 0xffffU));
    }
    assert((emitter.words[20] & 0xffffU) == 0xfe10U); // -496-byte frame
    assert((emitter.words[41] & 0xffffU) == 0x01f0U); // matching restore
    for (unsigned i = 0; i < emitter.words.size(); ++i) std::printf("%08x\n",emitter.words[i]);
    return 0;
}
