// SPDX-License-Identifier: GPL-2.0-or-later
// Actual launcher methods, host device/cache stubs. No Xbox executable is run.
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>
#define STB_TRUETYPE_IMPLEMENTATION
#include "stb_truetype.h"
#include "CclosLauncherTheme.h"
#include "CclosShellLayout.h"
typedef unsigned int DWORD; typedef unsigned char BYTE;
#define FAILED(x) ((x) < 0)
#define ZeroMemory(p,n) std::memset(p,0,n)
#ifdef _MSC_VER
#define _stricmp _stricmp
#else
#include <strings.h>
#define _stricmp strcasecmp
#endif
enum { FALSE=0, D3DRS_ZENABLE, D3DRS_ZWRITEENABLE, D3DRS_ALPHABLENDENABLE,
    D3DRS_CULLMODE, D3DRS_STENCILENABLE, D3DCULL_NONE,
    XINPUT_GAMEPAD_DPAD_UP=1, XINPUT_GAMEPAD_DPAD_DOWN=2,
    XINPUT_GAMEPAD_DPAD_LEFT=4, XINPUT_GAMEPAD_DPAD_RIGHT=8,
    XINPUT_GAMEPAD_LEFT_SHOULDER=256, XINPUT_GAMEPAD_RIGHT_SHOULDER=512,
    XINPUT_GAMEPAD_A=4096, XINPUT_GAMEPAD_B=8192,
    XINPUT_GAMEPAD_X=16384, XINPUT_GAMEPAD_Y=32768,
    XINPUT_GAMEPAD_TRIGGER_THRESHOLD=30, ERROR_SUCCESS=0 };
struct XINPUT_STATE { struct Pad { DWORD wButtons; short sThumbLX,sThumbLY; BYTE bRightTrigger; } Gamepad; } input;
static int XInputGetState(int, XINPUT_STATE *out) { *out=input; return 0; }
static int resourceCalls,scanCalls,writeCalls,cacheReads,descReads,drawCalls,triangles,animatedCalls;
static float fontAscent;
static double real_time_now() { ++animatedCalls; return 1; }
struct D3DVIEWPORT9 { int X,Y,Width,Height; float MinZ,MaxZ; };
struct Device {
    void SetViewport(D3DVIEWPORT9 *) {} void SetVertexDeclaration(void *) {}
    void SetVertexShader(void *) {} void SetPixelShader(void *) {}
    void SetTexture(int,void *) {} void SetRenderState(int,int) {}
} device;
static Device *pD3Ddevice=&device;
struct D3DSURFACE_DESC { unsigned int Width,Height; };
struct IDirect3DTexture9 {
    int id; unsigned int width,height; bool fail;
    int GetLevelDesc(int,D3DSURFACE_DESC *out) {
        ++descReads; if (fail) return -1;
        out->Width=width; out->Height=height; return 0;
    }
};
struct AtlasImage { int w,h; };
enum { I_DIR,I_UP_DIRECTORY,I_DIR_LINE,I_DROP_SHADOW,I_GRID,I_LINES,I_ICON,I_LOGO,I_BG,
       I_CROSS,I_CIRCLE,I_SQUARE,I_TRIANGLE };
struct Atlas { AtlasImage images[16]; } ui_atlas;
#ifdef REFERENCE_RENDER
static int FONT_H_LARGE,FONT_H_SMALL;
#endif
#include "launcher_constants.inc"
struct Command { std::string kind,text; float x,y,w,h; DWORD color; int scale,id; };
static std::vector<Command> commands;
static void record(const char *kind,float x,float y,float w,float h,DWORD color,const char *text="",int scale=1,int id=0) {
    Command c; c.kind=kind;c.text=text;c.x=x;c.y=y;c.w=w;c.h=h;c.color=color;c.scale=scale;c.id=id;
    commands.push_back(c); ++drawCalls;
    triangles+=c.kind=="text" ? (int)c.text.size()*2 : 2;
}
#ifdef CCLOS_IGM_TRACE
#include "cclos_ingame_stubs.h"
#endif
class XboxLauncher {
public:
    struct GameEntry { std::string path,filename,title; bool isDir,isGameFile; };
    enum Tab { TAB_RECENT,TAB_GAMES,TAB_COUNT };
    enum ViewMode { VIEW_LIST,VIEW_GRID };
    enum FocusRegion { FOCUS_TABS,FOCUS_GAMES,FOCUS_RIGHT_PANEL };
    bool active_,wantsSettings_,scanDone_,initFailed_;
    int selectedIndex_,scrollOffset_,rightPanelItem_,pollDelay_,repeatDelay_;
    Tab currentTab_; ViewMode viewMode_; FocusRegion focusRegion_;
    DWORD prevButtons_; BYTE prevRightTrigger_;
    std::string currentDir_,selectedGame_;
    std::vector<GameEntry> allGames_,recentGames_;
    void *vertexDecl_,*vertexShader_,*pixelShader_;
    IDirect3DTexture9 *zimTex_,*unknownTex_,*splashTex_;
    stbtt_packedchar *fontChars_;
    double startTime_; float symX_[100],symY_[100];
    bool missing;
#ifdef CCLOS_IGM_TRACE
    enum InGameMenuFocus { INGMENU_LEFT,INGMENU_RIGHT };
    bool inGameMenuActive_,wantsExitToMenu_,wantsExitToXbox_,wantsResetGame_;
    int inGameMenuSel_;InGameMenuFocus inGameMenuFocus_;DWORD igmPrevButtons_;
    char toastMsg_[64];DWORD toastEndTime_;
    void UpdateInGameMenu(DWORD);void RenderInGameMenu();void RenderToast();void ShowToast(const char*);
#include "ingame_state.inc"
#endif
    IDirect3DTexture9 covers[32];
    XboxLauncher() : active_(true),wantsSettings_(false),scanDone_(true),initFailed_(false),
        selectedIndex_(0),scrollOffset_(0),rightPanelItem_(0),pollDelay_(0),repeatDelay_(0),
        currentTab_(TAB_GAMES),viewMode_(VIEW_GRID),focusRegion_(FOCUS_GAMES),prevButtons_(0),prevRightTrigger_(0),
        currentDir_("game:\\PSP\\"),vertexDecl_(0),vertexShader_(0),pixelShader_(0),zimTex_(0),unknownTex_(0),splashTex_(0),
        fontChars_(0),startTime_(0),missing(false) {
#ifdef CCLOS_IGM_TRACE
        inGameMenuActive_=wantsExitToMenu_=wantsExitToXbox_=wantsResetGame_=false;
        inGameMenuSel_=0;inGameMenuFocus_=INGMENU_LEFT;igmPrevButtons_=0;toastMsg_[0]=0;toastEndTime_=0;
#endif
        for(int i=0;i<100;++i) { symX_[i]=(float)i; symY_[i]=(float)i; }
        for(int i=0;i<32;++i) { covers[i].id=i;covers[i].width=480;covers[i].height=272;covers[i].fail=false; }
    }
    void EnsureResources() { ++resourceCalls; }
    void ScanDirs() { ++scanCalls; }
    void PopulateCurrentDir() { ++scanCalls; }
    void SaveRecent() { ++writeCalls; }
    static bool IsGameFile(const char *) { return true; }
    IDirect3DTexture9 *GetOrCreatePoster(const std::string &path) {
        ++cacheReads;
        if(missing) return 0;
        unsigned int id=0;
        for(unsigned int i=0;i<path.size();++i) id=id*31+(unsigned char)path[i];
        return &covers[id%32];
    }
    IDirect3DTexture9 *GetOrCreateIcon(const std::string &) { ++cacheReads;return 0; }
    int StringWidth(const char *text,int scale) {
        float w=0;for(const char*p=text;*p;++p) {
            unsigned char c=(unsigned char)*p;
            w+= c>=32&&c<128 ? fontChars_[c-32].xadvance*(float)scale : 10.0f*(float)scale;
        }return(int)w;
    }
    void DrawString(const char *s,int x,int y,int scale,DWORD color) {
#ifndef REFERENCE_RENDER
        float pen=(float)x;
        for(const char *p=s;p&&*p;++p) {
            unsigned char ch=(unsigned char)*p;
            assert(ch>=32 && ch<128);
            const stbtt_packedchar &g=fontChars_[ch-32];
            // Match the actual DrawString quad geometry, not just advance widths.
            assert(pen+g.xoff*(float)scale>=64);
            assert(pen+g.xoff2*(float)scale<=1216);
            assert((float)y+(fontAscent+g.yoff)*(float)scale>=36);
            assert((float)y+(fontAscent+g.yoff2)*(float)scale<=684);
            pen+=g.xadvance*(float)scale;
        }
#endif
        if(s&&*s) record("text",(float)x,(float)y,(float)StringWidth(s,scale),20.0f*(float)scale,color,s,scale);
    }
    void DrawStringCentered(const char*s,int y,int scale,DWORD color) { DrawString(s,(1280-StringWidth(s,scale))/2,y,scale,color); }
    void DrawRect(float x,float y,float right,float bottom,DWORD color) { record("rect",x,y,right-x,bottom-y,color); }
    void DrawTexture(IDirect3DTexture9*t,float x,float y,float w,float h) { record("art",x,y,w,h,0xffffffff,"",1,t->id); }
    void DrawTextureAtlas(IDirect3DTexture9*,const AtlasImage&,float x,float y,float w,float h) { record("folder",x,y,w,h,0xffffffff); }
    void DrawTextureAtlasRotated(IDirect3DTexture9*,const AtlasImage&,float x,float y,float w,float h,float,DWORD color) { record("symbol",x,y,w,h,color); }
    void DrawShadow4Grid(IDirect3DTexture9*,const AtlasImage&,float x,float y,float right,float bottom,DWORD color,float) {
        record("shadow",x,y,right-x,bottom-y,color);triangles+=16;
    }
    void DrawFittedString(const char*,int,int,int,int,DWORD);
    void DrawFittedTexture(IDirect3DTexture9*,float,float,float,float);
    void RenderCclosBackground();
    void RenderTabBar(); void RenderGameList(); void RenderGrid(); void RenderRightPanel();
    void RenderGridItem(int,float,float,bool);void RenderListItem(int,float,bool);
    void RenderAnimatedBackground();void Render();void RenderSplash();void Update();
};
#include "launcher_methods.inc"
static void resetCounts() { commands.clear();resourceCalls=scanCalls=writeCalls=cacheReads=descReads=drawCalls=triangles=animatedCalls=0; }
static std::string quoted(const std::string &s) {
    std::ostringstream out;out<<'"';
    for(unsigned int i=0;i<s.size();++i) { unsigned char c=(unsigned char)s[i];
        if(c=='"'||c=='\\')out<<'\\'<<(char)c;
        else if(c<32||c>126)out<<'?';else out<<(char)c;
    }out<<'"';return out.str();
}
static void emit(const char *scene,int selection,const XboxLauncher &l) {
    std::cout<<"{\"scene\":"<<quoted(scene)<<",\"selection\":"<<selection<<",\"view\":"<<quoted(l.viewMode_==XboxLauncher::VIEW_LIST?"list":"grid")
        <<",\"drawCalls\":"<<drawCalls<<",\"triangles\":"<<triangles<<",\"cacheReads\":"<<cacheReads
        <<",\"descReads\":"<<descReads<<",\"animatedCalls\":"<<animatedCalls<<",\"commands\":[";
    for(unsigned int i=0;i<commands.size();++i) {
        const Command&c=commands[i];if(i)std::cout<<',';
        std::cout<<"{\"kind\":"<<quoted(c.kind)<<",\"text\":"<<quoted(c.text)<<",\"x\":"<<c.x<<",\"y\":"<<c.y<<",\"w\":"<<c.w<<",\"h\":"<<c.h
            <<",\"color\":"<<c.color<<",\"scale\":"<<c.scale<<",\"id\":"<<c.id<<'}';
    }std::cout<<"]}";
}
static void fixture(XboxLauncher &l,int count) {
    const char *names[]={"Orbital","Verdant","Afterglow","Tidal","Vector","Horizon","Lumen","Drift","Prism","Solstice","Echo","Wayfarer","Kinetic","Aerial"};
    for(int i=0;i<count;++i) { XboxLauncher::GameEntry e;e.title=names[i%14];e.filename=e.title+".iso";
        e.path="game:\\PSP\\"+e.filename;e.isDir=false;e.isGameFile=true;l.allGames_.push_back(e); }
    l.recentGames_=l.allGames_;
}
#ifndef CCLOS_IGM_TRACE
int main(int argc,char**argv) {
    assert(argc==2);
    std::ifstream file(argv[1],std::ios::binary);assert(file.good());
    std::vector<unsigned char> font((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());
    std::vector<unsigned char> pixels(512*512);stbtt_packedchar glyphs[96];stbtt_pack_context pc;
    assert(stbtt_PackBegin(&pc,&pixels[0],512,512,0,1,0));stbtt_PackSetOversampling(&pc,2,2);
    assert(stbtt_PackFontRange(&pc,&font[0],0,20,32,96,glyphs));stbtt_PackEnd(&pc);
    fontAscent=0;
    for(int i=0;i<96;++i) if(-glyphs[i].yoff>fontAscent) fontAscent=-glyphs[i].yoff;
#ifdef REFERENCE_RENDER
    float descent=0;
    for(int i=0;i<96;++i) if(glyphs[i].yoff2>descent) descent=glyphs[i].yoff2;
    FONT_H_LARGE=(int)((fontAscent+descent)*3);
    FONT_H_SMALL=(int)((fontAscent+descent)*2);
#endif
    for(int i=0;i<16;++i){ui_atlas.images[i].w=64;ui_atlas.images[i].h=48;}
    std::cout<<"[";bool first=true;
    for(int scene=0;scene<8;++scene) {
#if defined(REFERENCE_RENDER) && !defined(CCLOS_PREVIOUS_SHELL)
        if(scene>1) break;
#endif
        for(int view=0;view<2;++view) {
            if(scene==0 && view==1)continue;
            if(scene==1 && view==0)continue;
            XboxLauncher l;l.fontChars_=glyphs;fixture(l,scene==2?0:14);
            l.viewMode_=view?XboxLauncher::VIEW_LIST:XboxLauncher::VIEW_GRID;
            l.zimTex_=&l.covers[0];
            if(scene==3) l.missing=true;
            if(scene==4) {l.allGames_[0].title=std::string(4096,'W');l.allGames_[0].path=std::string(4096,'p');}
            if(scene==5) {l.allGames_[0].isDir=true;l.allGames_[0].title="PSP demos";}
            if(scene==6) {l.currentTab_=XboxLauncher::TAB_RECENT;l.viewMode_=XboxLauncher::VIEW_GRID;}
            if(scene==7) l.scanDone_=false;
            resetCounts();l.Render();
#ifndef REFERENCE_RENDER
            assert(animatedCalls==0 && writeCalls==0);
            for(unsigned int i=0;i<commands.size();++i) {
                const Command&c=commands[i];assert(c.x>=0 && c.y>=0 && c.w>=0 && c.h>=0);
                assert(c.x+c.w<=1280.01f && c.y+c.h<=720.01f);
                if(c.kind=="text") {assert(c.text.size()<=127);assert(c.x>=64 && c.y>=36);assert(c.x+c.w<=1216.01f && c.y+c.h<=684.01f);}
            }
#endif
            const char *names[]={"grid","list","empty","missing","long","folder","recent","loading"};
            if(!first) std::cout<<',';
            first=false;
            emit(names[scene],0,l);
        }
    }
#ifndef REFERENCE_RENDER
    XboxLauncher l;l.fontChars_=glyphs;fixture(l,32);l.selectedIndex_=17;l.scrollOffset_=4;
    ZeroMemory(&input,sizeof(input));input.Gamepad.bRightTrigger=100;
    resetCounts();l.Update();l.Update();assert(l.viewMode_==XboxLauncher::VIEW_LIST && l.selectedIndex_==17 && l.scrollOffset_==17);
    l.Update();l.Update();assert(l.viewMode_==XboxLauncher::VIEW_LIST);
    input.Gamepad.bRightTrigger=0;l.Update();l.Update();input.Gamepad.bRightTrigger=100;l.Update();l.Update();
    assert(l.viewMode_==XboxLauncher::VIEW_GRID && l.selectedIndex_==17 && l.scrollOffset_==
        (17 / GRID_COLS < ((32 + GRID_COLS - 1) / GRID_COLS - GRID_MAX_VISIBLE) ?
         17 / GRID_COLS : ((32 + GRID_COLS - 1) / GRID_COLS - GRID_MAX_VISIBLE)));
    assert(scanCalls==0 && writeCalls==0 && resourceCalls==0);
    // Navigate the full grid/list geometry, including last partial rows.
    for(int view=0;view<2;++view)for(int count=1;count<=32;++count) {
        XboxLauncher nav;nav.fontChars_=glyphs;fixture(nav,count);
        nav.viewMode_=view?XboxLauncher::VIEW_LIST:XboxLauncher::VIEW_GRID;
        for(int index=0;index<count;++index) {
            nav.selectedIndex_=index;
            nav.scrollOffset_=CclosShell::OffsetForSelection(index,count,view!=0);
            ZeroMemory(&input,sizeof(input));input.Gamepad.wButtons=XINPUT_GAMEPAD_DPAD_DOWN;
            nav.prevButtons_=0;nav.pollDelay_=0;resetCounts();nav.Update();nav.Update();
            int step=view?1:GRID_COLS;
            assert(nav.selectedIndex_==(index<count-step?index+step:index));
            int unit=view?nav.selectedIndex_:nav.selectedIndex_/GRID_COLS;
            int visible=view?LIST_H/LIST_ITEM_H:GRID_MAX_VISIBLE;
            assert(nav.scrollOffset_<=unit && unit<nav.scrollOffset_+visible);
            assert(scanCalls==0 && writeCalls==0 && resourceCalls==0);
        }
    }
    // Existing input contract: request a file, enter a folder, switch tabs, exit.
    // All side effects below are counters/strings in host stubs.
    for(int view=0;view<2;++view) {
        XboxLauncher game;fixture(game,32);game.fontChars_=glyphs;
        game.viewMode_=view?XboxLauncher::VIEW_LIST:XboxLauncher::VIEW_GRID;
        game.selectedIndex_=17;game.scrollOffset_=CclosLauncher::OffsetForSelection(17,32,view!=0);
        ZeroMemory(&input,sizeof(input));input.Gamepad.wButtons=XINPUT_GAMEPAD_A;
        resetCounts();game.Update();game.Update();
        assert(!game.active_ && game.selectedGame_==game.allGames_[17].path && writeCalls==1);
        XboxLauncher folder;fixture(folder,1);folder.allGames_[0].isDir=true;
        resetCounts();folder.Update();folder.Update();
        assert(folder.active_ && folder.currentDir_==folder.allGames_[0].path && scanCalls==1 && writeCalls==0);
        XboxLauncher tabs;fixture(tabs,14);tabs.viewMode_=XboxLauncher::VIEW_LIST;
        input.Gamepad.wButtons=XINPUT_GAMEPAD_RIGHT_SHOULDER;
        tabs.Update();tabs.Update();assert(tabs.currentTab_==XboxLauncher::TAB_RECENT && tabs.viewMode_==XboxLauncher::VIEW_GRID);
        input.Gamepad.wButtons=XINPUT_GAMEPAD_B;tabs.Update();tabs.Update();
        assert(!tabs.active_ && tabs.selectedGame_.empty());
    }
    l.active_=false;resetCounts();l.Render();l.Update();assert(commands.empty() && resourceCalls==0 && cacheReads==0);
    for(int count=0;count<=300;++count)for(int selected=-1;selected<=count+1;++selected)for(int view=0;view<2;++view) {
        int offset=CclosShell::OffsetForSelection(selected,count,view!=0);assert(offset>=0);
        if(count) {int clamped=selected<0?0:(selected>=count?count-1:selected);int unit=view?clamped:clamped/CclosShell::Columns;
            assert(offset<=unit && unit<offset+(view?CclosShell::ListRows:CclosShell::Rows));}
    }
    for(int width=0;width<1000;++width) {
        char out[128];std::string longTitle(10000,'W');CclosLauncher::FitText(longTitle.c_str(),out,glyphs,(float)width,1);
        assert(std::strlen(out)<=127 && l.StringWidth(out,1)<=width);
    }
    CclosLauncher::Rect fit;
    assert(!CclosLauncher::FitImage(0,10,0,0,100,100,fit));
    assert(CclosLauncher::FitImage(100,400,10,20,200,100,fit) && fit.w==25 && fit.h==100);
    assert(CclosLauncher::FitImage(400,100,10,20,200,100,fit) && fit.w==200 && fit.h==50);
    IDirect3DTexture9 bad={0,0,0,true};resetCounts();l.DrawFittedTexture(&bad,0,0,10,10);assert(commands.empty());
    char out[128];
    CclosLauncher::FitText("abc",out,(stbtt_packedchar*)0,100,1);assert(out[0]==0);
    CclosLauncher::FitText((const char*)0,out,glyphs,100,1);assert(out[0]==0);
    CclosLauncher::FitText("\xC3\xA9\n",out,glyphs,100,1);assert(std::strcmp(out,"???")==0);
    assert(CclosLauncher::OffsetForSelection(2147483646,2147483647,false)>=0);
#endif
    std::cout<<"]\n";return 0;
}
#endif
