// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <string>

namespace File {
bool Exists(const std::string &path);
bool Delete(const std::string &path);
}

namespace XenonBaseline {
// Paths come exclusively from the core's current-title slot-name generator.
// Preserve its savedata namespace and report partial deletion as a failure.
inline bool DeleteStateFiles(const std::string &state, const std::string &screenshot) {
    if (state.empty() || !File::Exists(state) || !File::Delete(state))
        return false;
    if (!screenshot.empty() && File::Exists(screenshot) && !File::Delete(screenshot))
        return false;
    return true;
}
}
