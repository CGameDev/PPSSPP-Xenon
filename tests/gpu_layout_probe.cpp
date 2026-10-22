// SPDX-License-Identifier: GPL-2.0-or-later
// Compile-only with the licensed PowerPC compiler; never execute on a console.
#include <stddef.h>
#include <ppcintrinsics.h>
#include "GPU/GPUState.h"
#define CHECK(name, condition) typedef char name[(condition) ? 1 : -1]
CHECK(state_size, sizeof(GPUgstate) == 1616);
CHECK(cache_size, sizeof(GPUStateCache) == 420);
CHECK(state_type_alignment, __alignof(GPUgstate) == 4);
CHECK(cache_type_alignment, __alignof(GPUStateCache) == 4);
CHECK(world_offset, offsetof(GPUgstate, worldMatrix) == 1024);
CHECK(view_offset, offsetof(GPUgstate, viewMatrix) == 1072);
CHECK(proj_offset, offsetof(GPUgstate, projMatrix) == 1120);
CHECK(tgen_offset, offsetof(GPUgstate, tgenMatrix) == 1184);
CHECK(bone_offset, offsetof(GPUgstate, boneMatrix) == 1232);
#ifdef EXPECT_ALIGNED_GLOBALS
CHECK(state_global_alignment, __alignof(gstate) == 16);
CHECK(cache_global_alignment, __alignof(gstate_c) == 16);
#else
CHECK(old_state_declaration_alignment, __alignof(gstate) == 4);
CHECK(old_cache_declaration_alignment, __alignof(gstate_c) == 4);
#endif
