// SPDX-License-Identifier: GPL-2.0-or-later
// Host-only test: the compatibility helper uses disposable files in the cwd.
#include <cstdio>
#include <string>
#include <fstream>
#include <cassert>
#include "../baseline-overlay/Xbox/XenonStateDeleteCompat.h"

namespace File {
std::string failPath;
bool Exists(const std::string &path) { std::ifstream f(path.c_str()); return f.good(); }
bool Delete(const std::string &path) {
    if (path == failPath) return false;
    return std::remove(path.c_str()) == 0;
}
}

static void create(const char *path) { std::ofstream f(path); f << "disposable fixture"; }

int main() {
    const std::string state = "selected.ppst", shot = "selected.jpg", other = "other.ppst";
    create(other.c_str());
    assert(!XenonBaseline::DeleteStateFiles("", shot));
    assert(!XenonBaseline::DeleteStateFiles(state, shot));
    create(state.c_str()); create(shot.c_str());
    File::failPath = state;
    assert(!XenonBaseline::DeleteStateFiles(state, shot));
    assert(File::Exists(state) && File::Exists(shot));
    File::failPath = shot;
    assert(!XenonBaseline::DeleteStateFiles(state, shot));
    assert(!File::Exists(state) && File::Exists(shot));
    create(state.c_str()); File::failPath.clear();
    assert(XenonBaseline::DeleteStateFiles(state, shot));
    assert(!File::Exists(state) && !File::Exists(shot) && File::Exists(other));
    create(state.c_str());
    assert(XenonBaseline::DeleteStateFiles(state, shot));
    assert(File::Exists(other));
    assert(File::Delete(other));
    std::puts("PASS: empty/missing paths, state/screenshot failure, successful deletion, absent screenshot, unrelated file preservation");
    return 0;
}
