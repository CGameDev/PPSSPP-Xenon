// SPDX-License-Identifier: GPL-2.0-or-later
// Actual extracted getBits, with explicit word-order emulation; no PPC code runs.
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
typedef unsigned char u8;
typedef unsigned int u32;
static unsigned int wordReads;
struct LittleWord {
    u8 b[4];
    operator u32() const { ++wordReads;return (u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24); }
};
struct BigWord {
    u8 b[4];
    operator u32() const { return ((u32)b[0]<<24)|((u32)b[1]<<16)|((u32)b[2]<<8)|b[3]; }
};
typedef LittleWord u32_le;
#define _dbg_assert_msg_(category,condition,format,value) assert(condition)
#include "pgf_current.inc"
#include "pgf_old_be.inc"
static u32 oracle(const u8 *data,int width,size_t pos) {
    u32 value=0;
    for(int i=0;i<width;++i) value|=(u32)((data[(pos+i)/8]>>((pos+i)%8))&1U)<<i;
    return value;
}
static u32 le32(const std::vector<u8>&data,size_t pos) { assert(pos+4<=data.size());return oracle(&data[0],32,pos*8); }
int main(int argc,char **argv) {
    assert(argc==19);
    std::vector<u8> bytes(64);
    for(size_t i=0;i<bytes.size();++i) bytes[i]=(u8)(i*73+19);
    unsigned int cases=0;
    for(int width=0;width<=32;++width)for(size_t bit=0;bit<256;++bit) {
        wordReads=0;
        assert((u32)currentGetBits(width,&bytes[0],bit)==oracle(&bytes[0],width,bit));
        unsigned int expected=width==0?0U:((bit%32)+(size_t)width<=32?1U:2U);
        assert(wordReads==expected);++cases;
    }
    // Last-word extraction must not read a second word when exactly on a boundary.
    u8 finalWord[4]={0x12,0x34,0x56,0xF8};wordReads=0;
    assert((u32)currentGetBits(32,finalWord,0)==0xF8563412U && wordReads==1);
    wordReads=0;assert(currentGetBits(0,0,0)==0 && wordReads==0);
    std::cout<<"{\"bit_cases\":"<<cases<<",\"fonts\":[";
    for(int file=1;file<argc;++file) {
        std::ifstream stream(argv[file],std::ios::binary);assert(stream.good());
        std::vector<u8> data((std::istreambuf_iterator<char>(stream)),std::istreambuf_iterator<char>());
        assert(data.size()>=392);
        u32 revision=le32(data,8),cmap=le32(data,16),count=le32(data,20),cmapBits=le32(data,24),pointerBits=le32(data,28);
        u32 shadow=le32(data,364),shadowBits=le32(data,368);
        size_t at=392,comp1=0,comp2=0;
        if(revision==3) {comp1=le32(data,396)&65535;comp2=le32(data,404)&65535;at+=20;}
        at+=8U*(data[258]+data[259]+data[260]+data[261]);
        at+=((shadow*shadowBits+31)&~31U)/8;at+=4*(comp1+comp2);
        size_t cmapAt=at;at+=((cmap*cmapBits+31)&~31U)/8;
        size_t fontStart=at+((count*pointerBits+31)&~31U)/8;
        assert(fontStart<data.size() && pointerBits>0 && pointerBits<32);
        size_t payload=data.size()-fontStart;
        unsigned int badOld=0,different=0;
        for(u32 i=0;i<cmap;++i) {
            assert((u32)currentGetBits((int)cmapBits,&data[cmapAt],(size_t)i*cmapBits)==oracle(&data[cmapAt],(int)cmapBits,(size_t)i*cmapBits));
        }
        for(u32 i=0;i<count;++i) {
            size_t bit=(size_t)i*pointerBits;
            u32 expected=oracle(&data[at],(int)pointerBits,bit);
            u32 actual=(u32)currentGetBits((int)pointerBits,&data[at],bit);
            u32 old=(u32)oldBigEndianGetBits((int)pointerBits,&data[at],bit);
            assert(actual==expected && (size_t)actual*4<payload);
            if((size_t)old*4>=payload)++badOld;
            if(actual!=old)++different;
        }
        assert(different>0 && badOld>0);
        if(file>1)std::cout<<',';
        std::cout<<"{\"glyphs\":"<<count<<",\"old_be_invalid_offsets\":"<<badOld<<",\"new_invalid_offsets\":0}";
    }
    std::cout<<"],\"word_reads_per_call\":\"0, 1 or 2; exact boundary does not overread\"}\n";
    return 0;
}
