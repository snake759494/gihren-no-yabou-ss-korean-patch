typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;
/* Subtitle data (tools/msub.py), copied to LWRAM at boot:
   u32 magic 'KSUB'; u32 nsub; u32 nmov; u32 off_fad; u32 off_subs; u32 off_gly; u32 off_txt
   fad[nmov]: start FAD of each subtitled movie file
   subs[nsub]: {u16 movie index; u16 start frame; u16 end frame; u16 text offset}  (15 fps video frames)
   gly: 11 u16 per glyph = 10 bitmap rows + advance
   txt: u16 glyph indices, 0xffff terminated */
#define D ((const u32*)0x002F3800)
#define FRAME (*(volatile u32*)0x0605A174)    /* current video frame of the movie overlay */
#define GFSTAG (*(volatile u32*)0x0605A2B0)   /* 'GFS ' tag followed by the GFS handle pointer */
#define GFSPTR (*(volatile u32*)0x0605A2B4)
#define VRAM ((volatile u32*)0x25E00000)      /* NBG0 RGB888 movie bitmap, 512 px per row */
#define Y0 228                                /* bitmap rows 228..239 = bottom black band */
static int cur=-1; static u32 lastfad, lastframe;
static void clear(void){ int y,x; for(y=Y0;y<Y0+12;y++) for(x=0;x<352;x++) VRAM[y*512+x]=0; }
static void draw(const u16 *gly,const u16 *t){
    int w=0,i,pass,n=(int)D[5];
    for(i=0;t[i]!=0xffff&&i<64;i++) w+=gly[t[i]*11+10];
    if(w>352) w=352;
    for(pass=0;pass<2;pass++){
        int x=(352-w)/2;
        for(i=0;t[i]!=0xffff&&i<64;i++){
            const u16 *g=gly+t[i]*11; int r,b;
            for(r=0;r<10;r++){ u16 bits=g[r];
                for(b=0;bits;b++,bits<<=1) if(bits&0x8000){
                    int px=x+b, py=Y0+1+r;
                    if(px<1||px>350) continue;
                    if(pass==0){ int dy,dx; for(dy=-1;dy<=1;dy++) for(dx=-1;dx<=1;dx++) VRAM[(py+dy)*512+px+dx]=0x80000000; }
                    else VRAM[py*512+px]=0x80FFFFFF;
                } }
            x+=g[10];
        }
    }
    (void)n;
}
void msub(void){
    u32 p,fad,frame; int i,m=-1,want=-1;
    if(D[0]!=0x4B535542) return;
    if(GFSTAG!=0x47465320) return;
    p=GFSPTR; if((p&3)||p<0x06000000||p>=0x06100000) return;
    fad=*(volatile u32*)(p+0x10); frame=FRAME;
    if(fad!=lastfad||frame<lastframe){ clear(); cur=-1; lastfad=fad; }
    lastframe=frame;
    { const u32 *f=(const u32*)((const u8*)D+D[3]); for(i=0;i<(int)D[2];i++) if(f[i]==fad){ m=i; break; } }
    if(m>=0){ const u16 *s=(const u16*)((const u8*)D+D[4]);
        for(i=0;i<(int)D[1];i++,s+=4) if(s[0]==m && frame>=s[1] && frame<s[2]){ want=i; break; } }
    if(want!=cur){
        clear();
        if(want>=0){ const u16 *s=(const u16*)((const u8*)D+D[4])+want*4;
            draw((const u16*)((const u8*)D+D[5]),(const u16*)((const u8*)D+D[6])+s[3]); }
        cur=want;
    }
}
