// SPDX-License-Identifier: GPL-2.0-or-later
// The real constructor and new overload are compiled against observable host stubs.
#include <cassert>
#include <cstdio>
struct MIPSState {};
struct CodeBlock {};
static int constructedMembers, initCalls;
struct JitBlockCache {
    MIPSState *mips; CodeBlock *codeBlock_; int *blocks; int num_blocks;
    JitBlockCache(MIPSState *, CodeBlock *);
    void Init() { assert(codeBlock_ && constructedMembers == 2); ++initCalls; }
#include "cache_init_method.inc"
};
#include "cache_constructor.inc"
struct Options {};
struct Registers {
    Registers(MIPSState *, Options * = 0) { ++constructedMembers; }
    void SetEmitter(CodeBlock *) {}
};
struct Jit : CodeBlock {
    JitBlockCache blocks; Options jo;
    Registers gpr, fpr; MIPSState *mips_;
    struct State { bool startDefaultPrefix; } js;
    Jit(MIPSState *);
    void AllocCodeSpace(int) { assert(initCalls == 1); }
    void GenerateFixedCode() { assert(blocks.codeBlock_ == this); }
};
#include "jit_constructor.inc"
int main() {
    MIPSState state; constructedMembers = initCalls = 0;
    Jit jit(&state);
    assert(jit.blocks.mips == &state && jit.mips_ == &state && jit.js.startDefaultPrefix);
    assert(jit.blocks.codeBlock_ == &jit && initCalls == 1);
    jit.blocks.Init(); // Existing no-argument reinitialization retains binding.
    assert(initCalls == 2 && jit.blocks.codeBlock_ == &jit);
    std::puts("PASS: cache binding after member construction and stable reinitialization");
    return 0;
}
