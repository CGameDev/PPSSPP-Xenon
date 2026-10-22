// SPDX-License-Identifier: GPL-2.0-or-later
// Launcher-only presentation. No resources, timers, persistence or emulator hooks.
#pragma once
namespace CclosLauncher {
static const unsigned int Canvas = 0xFF07131F;
static const unsigned int Panel = 0xFF101E30;
static const unsigned int Card = 0xFF102C3C;
static const unsigned int FocusCard = 0xFF153D43;
static const unsigned int Border = 0xFF294653;
static const unsigned int Teal = 0xFF5CE6D0;
static const unsigned int Text = 0xFFEAF6FA;
static const unsigned int Muted = 0xFFAEC7D3;
static const unsigned int Quiet = 0xFF7895A5;
static const int ContentTop = 184;
static const int ContentHeight = 416;
static const int GridWidth = 170;
static const int GridHeight = 124;
static const int Gap = 16;
static const int Columns = 4;
static const int Rows = 3;
static const int ListHeight = 52;
static const int ListRows = ContentHeight / ListHeight;

// View changes have different offset units (rows versus items).
inline int OffsetForSelection(int selected, int count, bool list) {
    if (count <= 0) return 0;
    if (selected < 0) selected = 0;
    if (selected >= count) selected = count - 1;
    int offset = list ? selected : selected / Columns;
    int limit = list ? count - ListRows : (count - 1) / Columns + 1 - Rows;
    if (limit < 0) limit = 0;
    return offset < limit ? offset : limit;
}

struct Rect { float x, y, w, h; };
inline bool FitImage(unsigned int sourceW, unsigned int sourceH,
                     float x, float y, float w, float h, Rect &out) {
    if (!sourceW || !sourceH || w <= 0 || h <= 0) return false;
    float scale = w / (float)sourceW;
    if ((float)sourceH * scale > h) scale = h / (float)sourceH;
    out.w = (float)sourceW * scale; out.h = (float)sourceH * scale;
    out.x = x + (w - out.w) * 0.5f; out.y = y + (h - out.h) * 0.5f;
    return true;
}

// One bounded pass over cached advances, no heap or repeated full-string scans.
// The current font atlas is ASCII; unsupported bytes use its question-mark glyph.
template<class Glyph>
inline void FitText(const char *text, char (&out)[128], const Glyph *glyphs,
                    float width, int scale) {
    out[0] = 0;
    if (!text || !glyphs || width <= 0 || scale <= 0) return;
    int n = 0;
    float used = 0;
    while (text[n] && n < 127) {
        unsigned char ch = (unsigned char)text[n];
        if (ch < 32 || ch >= 128) ch = '?';
        float advance = glyphs[ch - 32].xadvance * (float)scale;
        if (used + advance > width) break;
        out[n++] = (char)ch; used += advance;
    }
    if (text[n]) {
        float dots = glyphs['.' - 32].xadvance * (float)scale * 3;
        while (n && (used + dots > width || n > 124))
            used -= glyphs[(unsigned char)out[--n] - 32].xadvance * (float)scale;
        if (dots <= width) { out[n++] = '.'; out[n++] = '.'; out[n++] = '.'; }
    }
    out[n] = 0;
}
} // namespace CclosLauncher
