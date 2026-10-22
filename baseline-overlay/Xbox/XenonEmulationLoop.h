// SPDX-License-Identifier: GPL-2.0-or-later
// Owner emulation loop isolated from main's RAII objects; no per-frame call added.
#pragma once
#if defined(_MSC_VER)
#define XENON_SESSION_NOINLINE __declspec(noinline)
#else
#define XENON_SESSION_NOINLINE __attribute__((noinline))
#endif
static XENON_SESSION_NOINLINE bool RunEmulationSession(
    XboxLauncher &launcher, XboxHost *xbhost,
    bool &returnToMenu, bool &resetGame, bool &exitToXbox) {
	bool igmWasActive = false;
	__try
	{
		coreState = CORE_RUNNING;
		XINPUT_STATE igmState;
		ZeroMemory(&igmState, sizeof(igmState));
		while (coreState == CORE_RUNNING)
		{
			XInputGetState(0, &igmState);
			DWORD igmButtons = igmState.Gamepad.wButtons;
			BYTE igmLT = igmState.Gamepad.bLeftTrigger;
			BYTE igmRT = igmState.Gamepad.bRightTrigger;

			bool comboHeld = (igmButtons & XINPUT_GAMEPAD_LEFT_THUMB)
				&& igmLT > XINPUT_GAMEPAD_TRIGGER_THRESHOLD && igmRT > XINPUT_GAMEPAD_TRIGGER_THRESHOLD;

			static bool comboPrev = false;
			bool comboPressed = comboHeld && !comboPrev;
			comboPrev = comboHeld;

			if (comboPressed && !launcher.IsInGameMenuActive()) {
				launcher.SetInGameMenuActive(true);
			}

			// Fast forward: RB + RT, matching PPSSPP's fast-forward.
			// Unthrottling the emulator (which DoFrameTiming respects) makes
			// it run as fast as the CPU can go, and only while held.
			bool ffHeld = (igmButtons & XINPUT_GAMEPAD_RIGHT_SHOULDER)
				&& igmRT > XINPUT_GAMEPAD_TRIGGER_THRESHOLD;
			PSP_CoreParameter().unthrottle = ffHeld;

			if (launcher.IsInGameMenuActive()) {
				launcher.UpdateInGameMenu(igmButtons);
				launcher.RenderInGameMenu();

				xbhost->EndFrame();
				xbhost->SwapBuffers();
				xbhost->BeginFrame();

				static DWORD menuTick = 0;
				DWORD t = GetTickCount();
				if (menuTick > 0) {
					DWORD elapsed = t - menuTick;
					if (elapsed < 15) {
						Sleep(16 - (int)elapsed);
					}
				}
				menuTick = GetTickCount();

				if (launcher.WantsExitToMenu()) {
					launcher.ClearExitToMenu();
					returnToMenu = true;
					coreState = CORE_ERROR;
				} else if (launcher.WantsResetGame()) {
					launcher.ClearResetGame();
					resetGame = true;
					coreState = CORE_ERROR;
				} else if (launcher.WantsExitToXbox()) {
					launcher.ClearExitToXbox();
					exitToXbox = true;
					coreState = CORE_ERROR;
				}
			} else {
				// On transition from menu -> game, consume held buttons
				// so they don't leak through to the emulated PSP
				if (igmWasActive) {
					XInput.UpdateState(input_state);
					input_state.pad_last_buttons = input_state.pad_buttons;
				}

				u64 nowTicks = CoreTiming::GetTicks();
				u64 frameTicks = usToCycles(1000000/60);

				PSP_RunLoopUntil(nowTicks + frameTicks);

				UpdateInput(input_state);

				if (coreState == CORE_NEXTFRAME) {
					coreState = CORE_RUNNING;

				XboxFpsOverlay::DrawFpsOverlay();
				launcher.RenderToast();
				xbhost->EndFrame();
					xbhost->SwapBuffers();
					xbhost->BeginFrame();
				}
				igmWasActive = launcher.IsInGameMenuActive();
			}
		}
	}
	__except (LogCrashAndContinue(GetExceptionCode(), GetExceptionInformation()))
	{
		return false;
	}
	return true;
}
#undef XENON_SESSION_NOINLINE
