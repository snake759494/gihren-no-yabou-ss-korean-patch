typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;
register u8 *strp asm("r14");          /* caller's string pointer (all list renderers keep it in r14) */
extern const u8 kglyph[];
extern const u32 knum;
#define ORIG ((void(*)(int,int,void*,int))0x601462c)
#define REGP (*(u8**)0x603b8d4)
#define SLOT 0x1ff
#define VBASE 0x10800
/* entered from entry.s only for g in 0x4000..0x401f (Korean lead byte from the list renderers) */
void kdraw(int a,int g,void *pos,int col)
{
    u8 t = strp[1];
    if(!t) return;
    strp++;
    u32 k = (u32)(g-0x4000)*255u + (u32)(t-1);
    if(k >= knum) return;
    volatile u16 *dst=(volatile u16*)(0x25c00000+VBASE+k*32);
    const u16 *src=(const u16*)(kglyph+k*32);
    int i; for(i=0;i<16;i++) dst[i]=src[i];
    u16 *rec=(u16*)(REGP+SLOT*10);
    u16 s0=rec[0], s1=rec[1];
    rec[0]=(u16)((VBASE+k*32)>>3); rec[1]=0x0108;
    ORIG(a,SLOT,pos,col);
    rec[0]=s0; rec[1]=s1;
}
