// SPDX-License-Identifier: GPL-2.0-or-later
// Compiles the staged owner's menu input and actual presentation with host stubs.
#define CCLOS_IGM_TRACE
#include "cclos_launcher_trace.cpp"

static std::vector<std::string> transcript;
static void snapshot(const char *name,const XboxLauncher &l) {
    std::ostringstream text;
    text<<name<<'|'<<l.inGameMenuActive_<<'|'<<l.inGameMenuSel_<<'|'<<l.inGameMenuFocus_
        <<'|'<<l.wantsResetGame_<<l.wantsExitToXbox_<<l.wantsExitToMenu_
        <<'|'<<actionLog<<'|'<<l.toastMsg_<<'|'<<l.toastEndTime_<<'|'<<slotReads;
    transcript.push_back(text.str());
}
static void inputContracts() {
    hostTick=100;deleteResult=true;
    for(int slot=0;slot<SaveState::SAVESTATESLOTS;++slot)for(int occupied=0;occupied<2;++occupied) {
        for(int key=0;key<3;++key)for(int deletion=0;deletion<2;++deletion) {
            XboxLauncher l;l.SetInGameMenuActive(true);l.inGameMenuSel_=slot;
            savedMask=occupied?(1U<<slot):0;deleteResult=deletion!=0;resetServices();
            DWORD button=key==0?XINPUT_GAMEPAD_A:(key==1?XINPUT_GAMEPAD_X:XINPUT_GAMEPAD_Y);
            l.UpdateInGameMenu(button);snapshot("slot",l);
            if(key<2) {
                assert(!l.inGameMenuActive_ && l.toastEndTime_==2100);
                std::ostringstream expected;expected<<(key==0?'S':'L')<<slot<<";P;";
                assert(actionLog==expected.str());
                char expectedToast[32];std::sprintf(expectedToast,key==0?"State %d saved":"State %d loaded",slot+1);
                assert(std::strcmp(l.toastMsg_,expectedToast)==0);
            } else {
                assert(l.inGameMenuActive_);
                if(occupied) {
                    assert(actionLog.find("D:fixture-slot-")==0 && tickReads==1);
                    char expectedToast[32];std::sprintf(expectedToast,deletion?"State %d deleted":"Delete state %d failed",slot+1);
                    assert(std::strcmp(l.toastMsg_,expectedToast)==0);
                } else assert(actionLog.empty() && l.toastMsg_[0]==0);
            }
            std::string before=actionLog;l.UpdateInGameMenu(button);
            assert(actionLog==before);snapshot("held",l);
        }
    }
    for(int item=0;item<5;++item) {
        XboxLauncher l;l.SetInGameMenuActive(true);l.inGameMenuFocus_=XboxLauncher::INGMENU_RIGHT;l.inGameMenuSel_=item;
        resetServices();l.UpdateInGameMenu(XINPUT_GAMEPAD_A);
        assert(!l.inGameMenuActive_ && actionLog.empty());
        assert(l.wantsResetGame_==(item==2) && l.wantsExitToXbox_==(item==3) && l.wantsExitToMenu_==(item==4));
        snapshot("session",l);
    }
    for(int panel=0;panel<2;++panel)for(int item=0;item<5;++item) {
        XboxLauncher l;l.SetInGameMenuActive(true);l.inGameMenuFocus_=panel?XboxLauncher::INGMENU_RIGHT:XboxLauncher::INGMENU_LEFT;l.inGameMenuSel_=item;
        resetServices();l.UpdateInGameMenu(XINPUT_GAMEPAD_A|XINPUT_GAMEPAD_B);
        assert(!l.inGameMenuActive_ && actionLog.empty() && !l.wantsResetGame_ && !l.wantsExitToMenu_ && !l.wantsExitToXbox_);
        snapshot("cancel",l);
    }
    XboxLauncher nav;nav.SetInGameMenuActive(true);resetServices();
    for(int i=0;i<8;++i) {nav.UpdateInGameMenu(0);nav.UpdateInGameMenu(XINPUT_GAMEPAD_DPAD_DOWN);}
    assert(nav.inGameMenuSel_==SaveState::SAVESTATESLOTS-1);
    nav.UpdateInGameMenu(XINPUT_GAMEPAD_DPAD_RIGHT);assert(nav.inGameMenuFocus_==XboxLauncher::INGMENU_RIGHT);
    nav.UpdateInGameMenu(0);nav.UpdateInGameMenu(XINPUT_GAMEPAD_DPAD_LEFT);assert(nav.inGameMenuFocus_==XboxLauncher::INGMENU_LEFT);
    for(int i=0;i<8;++i) {nav.UpdateInGameMenu(0);nav.UpdateInGameMenu(XINPUT_GAMEPAD_DPAD_UP);}
    assert(nav.inGameMenuSel_==0 && actionLog.empty());snapshot("navigation",nav);
    nav.wantsResetGame_=nav.wantsExitToMenu_=nav.wantsExitToXbox_=true;
    nav.SetInGameMenuActive(true);assert(!nav.wantsResetGame_&&!nav.wantsExitToMenu_&&!nav.wantsExitToXbox_);
    nav.SetInGameMenuActive(false);resetServices();resetCounts();nav.UpdateInGameMenu(XINPUT_GAMEPAD_A);nav.RenderInGameMenu();nav.RenderToast();
    assert(actionLog.empty() && tickReads==0 && slotReads==0 && resourceCalls==0 && commands.empty());snapshot("inactive",nav);
}

int main(int argc,char **argv) {
    assert(argc==2);
    std::ifstream file(argv[1],std::ios::binary);assert(file.good());
    std::vector<unsigned char> font((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());
    std::vector<unsigned char> pixels(512*512);stbtt_packedchar glyphs[96];stbtt_pack_context pc;
    assert(stbtt_PackBegin(&pc,&pixels[0],512,512,0,1,0));stbtt_PackSetOversampling(&pc,2,2);
    assert(stbtt_PackFontRange(&pc,&font[0],0,20,32,96,glyphs));stbtt_PackEnd(&pc);
    fontAscent=0;
    for(int i=0;i<96;++i) fontAscent=std::max(fontAscent,-glyphs[i].yoff);
#ifdef REFERENCE_RENDER
    float descent=0;
    for(int i=0;i<96;++i) descent=std::max(descent,glyphs[i].yoff2);
    FONT_H_SMALL=(int)((fontAscent+descent)*2);FONT_H_LARGE=(int)((fontAscent+descent)*3);
#endif
    for(int i=0;i<16;++i){ui_atlas.images[i].w=64;ui_atlas.images[i].h=48;}
    inputContracts();
    std::cout<<"{\"frames\":[";bool first=true;
    for(int mask=0;mask<3;++mask)for(int focus=0;focus<2;++focus)for(int selected=0;selected<5;++selected) {
        XboxLauncher l;l.fontChars_=glyphs;l.zimTex_=&l.covers[0];fixture(l,14);
        l.SetInGameMenuActive(true);l.inGameMenuFocus_=focus?XboxLauncher::INGMENU_RIGHT:XboxLauncher::INGMENU_LEFT;l.inGameMenuSel_=selected;
        savedMask=mask==0?5U:(mask==1?0U:31U);hostTick=100;resetServices();resetCounts();l.RenderInGameMenu();
        assert(slotReads==SaveState::SAVESTATESLOTS && actionLog.empty() && cacheReads==0 && descReads==0 && scanCalls==0 && writeCalls==0);
#ifndef REFERENCE_RENDER
        assert(animatedCalls==0);
        for(unsigned int i=0;i<commands.size();++i) {
            const Command &c=commands[i];assert(c.x>=0 && c.y>=0 && c.x+c.w<=1280 && c.y+c.h<=720);
        }
#endif
        if(!first)std::cout<<',';
        first=false;
        const char *names[]={"menu-mixed","menu-empty","menu-saved"};emit(names[mask],focus*5+selected,l);
    }
    for(int i=0;i<3;++i) {
        XboxLauncher l;l.fontChars_=glyphs;l.zimTex_=&l.covers[0];l.SetInGameMenuActive(true);savedMask=5;hostTick=0;
        l.ShowToast(i==2?std::string(4096,'W').c_str():"State 1 saved");hostTick=i==1?1750:0;
        resetServices();resetCounts();l.RenderInGameMenu();
        assert(slotReads==5 && actionLog.empty() && cacheReads==0);
        const char *names[]={"menu-toast","menu-toast-fade","menu-toast-long"};std::cout<<',';emit(names[i],0,l);
    }
    {
        XboxLauncher l;l.fontChars_=glyphs;l.SetInGameMenuActive(true);savedMask=5;
        resetServices();resetCounts();l.RenderInGameMenu();
        assert(slotReads==5 && cacheReads==0 && actionLog.empty());std::cout<<',';emit("menu-no-atlas",0,l);
    }
    const DWORD times[]={0,1499,1500,1750,1999,2000,2001};
    for(unsigned int i=0;i<sizeof(times)/sizeof(times[0]);++i) {
        XboxLauncher l;l.fontChars_=glyphs;hostTick=0;l.ShowToast("State 1 saved");hostTick=times[i];resetServices();resetCounts();l.RenderToast();
        if(hostTick<2000) {assert(l.toastMsg_[0] && resourceCalls==1 && tickReads==1);}
        else assert(l.toastMsg_[0]==0 && commands.empty() && resourceCalls==0);
        assert(slotReads==0 && actionLog.empty() && cacheReads==0);
        std::ostringstream scene;scene<<"toast-"<<hostTick;std::cout<<',';emit(scene.str().c_str(),0,l);
#ifndef REFERENCE_RENDER
        if(hostTick==1750) {assert(commands[0].color>>24==90);assert(commands.back().color>>24==127);}
#endif
    }
    XboxLauncher longToast;longToast.fontChars_=glyphs;hostTick=0;
    longToast.ShowToast(std::string(4096,'W').c_str());assert(std::strlen(longToast.toastMsg_)==63);
    resetCounts();longToast.RenderToast();std::cout<<',';emit("toast-long",0,longToast);
    std::cout<<"],\"input_transcript\":[";
    for(unsigned int i=0;i<transcript.size();++i) {if(i)std::cout<<',';std::cout<<quoted(transcript[i]);}
    std::cout<<"]}\n";
    return 0;
}
