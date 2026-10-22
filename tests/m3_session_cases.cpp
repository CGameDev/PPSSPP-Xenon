// SPDX-License-Identifier: GPL-2.0-or-later
// The actual loop runs against host stubs. Native MSVC tests use real host SEH.
#include <cassert>
#include <cstring>
#include <cstdio>
#ifdef _MSC_VER
#include <windows.h>
#else
typedef unsigned int DWORD; typedef unsigned char BYTE;
#define ZeroMemory(p,n) std::memset(p,0,n)
#define __try try
#define __except(filter) catch (int)
#endif
#define GetTickCount FixtureGetTickCount
#define Sleep FixtureSleep
typedef unsigned long long u64;
enum { CORE_RUNNING, CORE_ERROR, CORE_NEXTFRAME };
enum { XINPUT_GAMEPAD_LEFT_THUMB = 1, XINPUT_GAMEPAD_RIGHT_SHOULDER = 2,
       XINPUT_GAMEPAD_TRIGGER_THRESHOLD = 30 };
struct XINPUT_STATE {
    struct Pad { DWORD wButtons; BYTE bLeftTrigger, bRightTrigger; } Gamepad;
};
static int coreState, scenario, inputCalls, menuUpdates, renders, frames, consumed, runs, filterCalls;
static DWORD tick;
struct Input { int pad_last_buttons, pad_buttons; } input_state;
struct Parameter { bool unthrottle; } parameter;
static Parameter &PSP_CoreParameter() { return parameter; }
static void XInputGetState(int, XINPUT_STATE *state) {
    ++inputCalls;
    state->Gamepad.wButtons = scenario == 1 ? XINPUT_GAMEPAD_LEFT_THUMB : 0;
    state->Gamepad.bLeftTrigger = state->Gamepad.bRightTrigger = scenario == 1 ? 100 : 0;
    if (scenario == 5) { state->Gamepad.wButtons = XINPUT_GAMEPAD_RIGHT_SHOULDER; state->Gamepad.bRightTrigger = 100; }
}
static DWORD GetTickCount() { return ++tick; }
static void Sleep(int) {}
struct XboxHost {
    void EndFrame() { ++frames; }
    void SwapBuffers() { ++frames; }
    void BeginFrame() { ++frames; }
};
struct XboxLauncher {
    bool menu;
    bool IsInGameMenuActive() { return menu; }
    void SetInGameMenuActive(bool active) { menu = active; }
    void UpdateInGameMenu(DWORD) { ++menuUpdates; if (scenario == 6) menu = false; }
    void RenderInGameMenu() { ++renders; }
    bool WantsExitToMenu() { return scenario == 1 || scenario == 2; }
    bool WantsResetGame() { return scenario == 3; }
    bool WantsExitToXbox() { return scenario == 4; }
    void ClearExitToMenu() {}
    void ClearResetGame() {}
    void ClearExitToXbox() {}
    void RenderToast() { ++renders; }
};
static XboxLauncher *activeLauncher;
namespace CoreTiming { static u64 GetTicks() { return 123; } }
static u64 usToCycles(int value) { return (u64)value; }
static int LogCrashAndContinue(unsigned int, void *) { ++filterCalls; return 1; }
#ifndef _MSC_VER
#define GetExceptionCode() 0U
#define GetExceptionInformation() ((void *)0)
#endif
static void PSP_RunLoopUntil(u64) {
    ++runs;
    if (scenario == 6 && runs == 1) activeLauncher->menu = true;
    if (scenario == 7) {
#ifdef _MSC_VER
        RaiseException(0xE0000001, 0, 0, NULL);
#else
        throw 1;
#endif
    }
    coreState = runs == 1 ? CORE_NEXTFRAME : CORE_ERROR;
}
struct InputDevice { void UpdateState(Input &input) { ++consumed; input.pad_buttons = 17; } } XInput;
static void UpdateInput(Input &) {}
namespace XboxFpsOverlay { static void DrawFpsOverlay() {} }
#include "XenonEmulationLoop.h"
int main() {
    (void)&LogCrashAndContinue;
    // Run first-frame execution, menu return/reset/exit, fast-forward, resume and host fault paths.
    for (scenario = 0; scenario <= 7; ++scenario) {
        inputCalls = menuUpdates = renders = frames = consumed = runs = filterCalls = 0;
        bool returnToMenu = false, resetGame = false, exitToXbox = false;
        XboxHost host; XboxLauncher launcher;
        launcher.menu = (scenario >= 2 && scenario <= 4);
        activeLauncher = &launcher;
        bool ok = RunEmulationSession(launcher, &host, returnToMenu, resetGame, exitToXbox);
        assert(ok == (scenario != 7));
        assert(returnToMenu == (scenario == 1 || scenario == 2));
        assert(resetGame == (scenario == 3)); assert(exitToXbox == (scenario == 4));
        if (scenario >= 1 && scenario <= 4) assert(runs == 0 && menuUpdates == 1);
        if (scenario == 0 || scenario == 5) assert(runs == 2 && frames == 3);
        if (scenario == 5) assert(parameter.unthrottle);
        if (scenario == 6) assert(consumed == 1 && input_state.pad_last_buttons == 17);
        if (scenario == 7) {
#ifdef _MSC_VER
            assert(filterCalls == 1);
#endif
        }
    }
    std::puts("PASS: 8 actual session-loop cases (host stubs; no Xbox execution)");
    return 0;
}
