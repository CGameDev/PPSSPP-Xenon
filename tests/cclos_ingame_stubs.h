// SPDX-License-Identifier: GPL-2.0-or-later
// Host-only state service: strings/counters only; no files, Xbox or PSP execution.
static DWORD hostTick;
static int tickReads,slotReads;
static unsigned int savedMask;
static bool deleteResult;
static std::string actionLog;
static DWORD GetTickCount() { ++tickReads;return hostTick; }
static void action(char kind,int slot) {
    std::ostringstream text;text<<kind<<slot<<';';actionLog+=text.str();
}
namespace SaveState {
#include "save_slots.inc"
static bool HasSaveInSlot(int slot) { ++slotReads;assert(slot>=0 && slot<SAVESTATESLOTS);return (savedMask&(1U<<slot))!=0; }
static void SaveSlot(int slot,int,int) { action('S',slot); }
static void LoadSlot(int slot,int,int) { action('L',slot); }
static void Process() { actionLog+="P;"; }
static std::string GenerateSaveSlotFilename(int slot,const char *extension) {
    std::ostringstream text;text<<"fixture-slot-"<<slot<<'.'<<extension;return text.str();
}
}
namespace XenonBaseline {
static bool DeleteStateFiles(const std::string &state,const std::string &image) {
    actionLog+="D:"+state+":"+image+";";return deleteResult;
}
}
static void resetServices() { tickReads=slotReads=0;actionLog.clear(); }
