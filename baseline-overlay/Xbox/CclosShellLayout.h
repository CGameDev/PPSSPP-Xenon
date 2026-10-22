// SPDX-License-Identifier: GPL-2.0-or-later
// Approved shell geometry only; no resources, clocks or emulator hooks.
#pragma once
namespace CclosShell {
static const int Columns = 3;
static const int Rows = 2;
static const int GridWidth = 208;
static const int GridHeight = 192;
static const int ContentHeight = 416;
static const int ListHeight = 68;
static const int ListRows = ContentHeight / ListHeight;
inline int OffsetForSelection(int selected, int count, bool list) {
    if (count <= 0) return 0;
    if (selected < 0) selected = 0;
    if (selected >= count) selected = count - 1;
    int offset = list ? selected : selected / Columns;
    int limit = list ? count - ListRows : (count - 1) / Columns + 1 - Rows;
    if (limit < 0) limit = 0;
    return offset < limit ? offset : limit;
}
}
