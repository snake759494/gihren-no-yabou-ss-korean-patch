import sys,os,json,glob,struct,shutil,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mfdpack import split,decode,encode,join
from cont import parse,build as cbuild,pack as cpack,Node
from render import render_line,to_strip
from cdimg import Image
from img4 import sub_entries
from helpimg import render as help_render
from lzenc import compress
from retext import retext,palette
from uilabel import dec_lab,enc_lab,label as ui_label,bar2,name_label,map_legend,map_button,map_lr
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT=os.path.dirname(W)
BASE='Kidou Senshi Gundam - Gihren no Yabou (Japan)'
OUTB=os.environ.get('OUTB','Kidou Senshi Gundam - Gihren no Yabou (Korean)')
FONT=('NanumSquareNeo-cBd.ttf',15)
def load_ko():
    ko={}
    for f in sorted(glob.glob(os.path.join(W,'ko','*.json'))):
        ko.update({int(k):v for k,v in json.load(open(f,encoding='utf8')).items()})
    return ko
def leaf_at(node,path):
    for p in path: node=node.kids[p]
    return node
def outlined(lines_ja,i,orig_px):
    # alt (outline) style if no pixel value 15 in original strip
    return not any((b>>4)==15 or (b&15)==15 for b in orig_px)
def build_scenes(ko,img,ents_dir,report):
    L=json.load(open(os.path.join(W,'lines_ja.json'),encoding='utf8'))
    byfile={}
    for i,l in enumerate(L):
        if i in ko: byfile.setdefault(l['file'],[]).append((i,l))
    changed={}
    for decname,items in byfile.items():
        mfdname=decname.rsplit('_',1)[0]+'.MFD'; eidx=int(decname.rsplit('_',1)[1][:-4])
        if mfdname not in changed:
            changed[mfdname]=split(open(os.path.join(W,'disc',mfdname),'rb').read())
        ents,last=changed[mfdname]
        data=decode(ents[eidx]); root=parse(data)
        # keep every top-level kid except the strip block (kid 1) as original bytes
        c=struct.unpack_from('>I',data,0)[0]; offs=struct.unpack_from('>%dI'%c,data,4)
        pad=data+bytes(256)
        for k in range(c):
            if k==1: continue
            sz=struct.unpack_from('>I',pad,offs[k]-4)[0]
            root.kids[k]=Node(data=pad[offs[k]:offs[k]+sz])
        for i,l in items:
            leaf=leaf_at(root,l['path'])
            w,h=struct.unpack_from('>HH',leaf.data,0)
            text=ko[i]
            q,cells=render_line(text,*FONT,outline=outlined(L,i,leaf.data[4:4+w*h//2]))
            if cells>20: report.append(f'OVER {i} {cells} {text}')
            px,cells=to_strip(q)
            leaf.data=struct.pack('>HH',16,16*cells)+px
        nd=cbuild(root)
        ents[eidx]['new']=encode(ents[eidx],nd)
    return changed
def build_help(changed,report):
    ko={}
    for f in glob.glob(os.path.join(W,'help','*.json')): ko.update(json.load(open(f,encoding='utf8')))
    by={}
    for key,v in ko.items():
        fam,e,i=key.rsplit('_',2); by.setdefault((fam,int(e)),{})[int(i)]=v
    only=os.environ.get('HELPONLY','')
    for (fam,e),items in sorted(by.items()):
        if only and not fam.startswith(tuple(only.split(','))): continue
        mfdname=fam+'.MFD'
        if mfdname not in changed: changed[mfdname]=split(open(os.path.join(W,'disc',mfdname),'rb').read())
        ents,last=changed[mfdname]
        data=decode(ents[e])
        c=struct.unpack_from('>I',data,0)[0]; offs=struct.unpack_from('>%dI'%c,data,4)
        pad=data+bytes(256); parts=[]
        subs=sub_entries(data)
        for k,o in enumerate(offs):
            sz=struct.unpack_from('>I',pad,o-4)[0]
            if k in items:
                out=subs[k][3]; w,h=struct.unpack_from('>HH',out,0); out=out+bytes(max(0,w*h//2+4-len(out)))
                nb,info=help_render(out,items[k]['title'],items[k]['body'])
                cc,g,left=compress(nb); assert left==0
                parts.append(struct.pack('>HH',subs[k][1],g)+cc)
            else: parts.append(pad[o:o+sz])
        ents[e]['new']=encode(ents[e],cpack(parts))
def build_ui(changed,report):
    """menu/panel/label bitmaps: ui_ko.json (palette retext), labels_ko.json, msg_ko.json, panels_ko.json"""
    U=os.path.join(W,'ui')
    J=lambda n: json.load(open(os.path.join(U,n),encoding='utf8'))
    cfg_rt=J('ui_ko.json'); cfg_lb=J('labels_ko.json'); cfg_msg=J('msg_ko.json'); cfg_pn=J('panels_ko.json')
    decs=sorted(set(cfg_rt)|set(cfg_lb)|set(cfg_msg)|set(cfg_pn))
    for dec in decs:
        mfdname=dec.rsplit('_',1)[0]+'.MFD'; e=int(dec.rsplit('_',1)[1])
        if mfdname not in changed: changed[mfdname]=split(open(os.path.join(W,'disc',mfdname),'rb').read())
        ents,_=changed[mfdname]
        data=decode(ents[e]) if 'new_data' not in ents[e] else ents[e]['new_data']
        root=parse(data)
        if dec in cfg_rt:
            c=cfg_rt[dec]; hd=c.get('hdr',0)
            for k,it in c['items'].items():
                kid=root.kids[int(k)]; pal=palette(root.kids[int(c['pal'][k])].data)
                nb,res=retext(kid.data[hd:],pal,it['box'],it['text'],it['font'],it['size'],it.get('align','left'),it.get('outline',True),
                              glow=it.get('glow',False),xoff=it.get('xoff',0),rowmode=it.get('rowmode'))
                kid.data=kid.data[:hd]+nb
        if dec in cfg_lb:
            c=cfg_lb[dec]
            for k,t in c['items'].items():
                kid=root.kids[int(k)]; kid.data=enc_lab(kid.data,ui_label(dec_lab(kid.data),t,c['align'],ink=c.get('ink')))
        if dec in cfg_msg:
            for k,v in cfg_msg[dec].items():
                kid=root.kids[int(k)]; nb,info=help_render(kid.data[4:],v['title'],v['body']); kid.data=kid.data[:4]+nb
        if dec in cfg_pn:
            for k,items in cfg_pn[dec].items():
                kid=root.kids[int(k)]; a=dec_lab(kid.data)
                for it in items:
                    y0,y1,x0,x1,t=it[:5]; tx=it[5] if len(it)>5 else None; fn=it[6] if len(it)>6 else None; rf=it[7] if len(it)>7 else None
                    a=bar2(a,y0,y1,x0,x1,t,tx,font=fn,ref=rf)
                kid.data=enc_lab(kid.data,a)
        nd=cbuild(root)
        ents[e]['new_data']=nd
        ents[e]['new']=encode(ents[e],nd)
def build_names(changed,report):
    N=os.path.join(W,'names')
    ko={}
    for f in sorted(glob.glob(os.path.join(N,'names_*.json'))): ko.update({int(k):v for k,v in json.load(open(f,encoding='utf8')).items()})
    meta=json.load(open(os.path.join(N,'unique.json'))); items=json.load(open(os.path.join(N,'items.json')))
    h2id={m['hash']:m['id'] for m in meta}
    byfile={}
    for it in items:
        i=h2id[it['hash']]
        if i in ko: byfile.setdefault(it['file'],[]).append((it['kid'],i))
    import hashlib
    for dec,lst in sorted(byfile.items()):
        mfdname=dec.rsplit('_',1)[0]+'.MFD'; e=int(dec.rsplit('_',1)[1][:-4])
        if mfdname not in changed: changed[mfdname]=split(open(os.path.join(W,'disc',mfdname),'rb').read())
        ents,_=changed[mfdname]
        data=ents[e]['new_data'] if 'new_data' in ents[e] else decode(ents[e])
        root=parse(data)
        for kid,i in lst:
            node=root.kids[kid]; a=dec_lab(node.data); t=ko[i]
            if i==257: n=bar2(a,6,18,6,60,t,ink=1)
            elif 260<=i<=265: n=map_legend(a,t)
            elif i in (266,267): n=map_button(a,t)
            elif 268<=i<=270: n=map_lr(a,t)
            else: n=name_label(a,t)
            node.data=enc_lab(node.data,n)
        nd=cbuild(root); ents[e]['new_data']=nd; ents[e]['new']=encode(ents[e],nd)
def build_bram(changed,report):
    from bram import load,store,retext_bram
    T=json.load(open(os.path.join(W,'ui','bram_ko.json'),encoding='utf8'))
    if 'BRAM_ERR.MFD' not in changed: changed['BRAM_ERR.MFD']=split(open(os.path.join(W,'disc','BRAM_ERR.MFD'),'rb').read())
    ents,_=changed['BRAM_ERR.MFD']
    for i,e in enumerate(ents):
        if str(i) not in T: continue
        data=decode(e); root=parse(data)
        img,pal,m=load(root); n0=len(set(m.reshape(-1)))
        out,nl=retext_bram(img,pal,T[str(i)])
        n1=store(root,out)
        report.append(f'BRAM {i} cells {n0}->{n1}')
        nd=cbuild(root); e['new_data']=nd; e['new']=encode(e,nd)
def build_hekik(changed,report):
    from hekik import decode_kid,encode_kid,render as hk_render
    H=os.path.join(W,'hekik')
    ko={}
    for f in sorted(glob.glob(os.path.join(H,'ko_*.json'))): ko.update({int(k):v for k,v in json.load(open(f,encoding='utf8')).items()})
    if not ko: return
    ids=json.load(open(os.path.join(H,'ids.json'))); items=json.load(open(os.path.join(H,'items.json')))
    h2i={h:i for i,h in enumerate(ids)}
    byfile={}
    for it in items:
        i=h2i[it['hash']]
        if i in ko: byfile.setdefault(it['file'],[]).append((it['kid'],i))
    for dec,lst in sorted(byfile.items()):
        mfdname=dec.rsplit('_',1)[0]+'.MFD'; e=int(dec.rsplit('_',1)[1][:-4])
        if mfdname not in changed: changed[mfdname]=split(open(os.path.join(W,'disc',mfdname),'rb').read())
        ents,_=changed[mfdname]
        data=ents[e]['new_data'] if 'new_data' in ents[e] else decode(ents[e])
        root=parse(data)
        for kid,i in lst:
            node=root.kids[kid]; mark,hdr,a=decode_kid(node.data)
            n,info=hk_render(a,ko[i]['title'],ko[i]['body'])
            if not info[0]: report.append(f'HEKIK {i} small font {info}')
            node.data=encode_kid(mark,hdr,n)
        nd=cbuild(root); ents[e]['new_data']=nd; ents[e]['new']=encode(ents[e],nd)
def msub_parts():
    """(code, LWRAM data) for the movie subtitles, or empty when disabled."""
    import msub
    f=os.path.join(W,'msub','subs.json')
    if 'msub' not in os.environ.get('PARTS','msub') or not os.path.exists(f): return b'',b''
    fads={}
    for l in open(os.path.join(W,'files.txt')):
        lba,sz,n=l.split(); n=n.strip('/').split(';')[0]
        if n.startswith('MOVIE') and n.endswith('.CAK'): fads[int(n[5:8])]=int(lba)+150
    return msub.code(),msub.build(json.load(open(f,encoding='utf8')),fads)
def build_glyph16(changed,report):
    import glyph16
    name='DATA02.MFD'
    if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
    ent=changed[name][0][2]
    d=ent['new_data'] if 'new_data' in ent else decode(ent)
    n=parse(d); glyph16.patch(n.kids); nd=cbuild(n)
    ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append(f'G16 {len(d)}->{len(nd)}')
    for name in ('PROG01.MFD','PROG03.MFD'):
        if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
        ent=changed[name][0][0]
        d=ent['new_data'] if 'new_data' in ent else decode(ent)
        nd=glyph16.patch_rank(d); ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append('RANK glyphs')
def build_ending(changed,report):
    """ENDINGxx.MFD entry1: scrolling ending text image (280x960 4bpp)"""
    import ending
    K=ending.load(W)
    for k,paras in sorted(K.items()):
        name='ENDING%s.MFD'%k
        if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
        ent=changed[name][0][1]
        d=ent['new_data'] if 'new_data' in ent else decode(ent)
        q,n=ending.render(paras); nd=ending.pack(q); assert len(nd)==len(d)
        ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append(f'ENDING {len(K)}')
def build_mapframe(changed,report):
    import mapframe
    for f in sorted(glob.glob(os.path.join(W,'disc','MAP*_Z*.MFD'))):
        name=os.path.basename(f)
        if name not in changed: changed[name]=split(open(f,'rb').read())
        ent=changed[name][0][0]
        d=ent['new_data'] if 'new_data' in ent else decode(ent)
        root=parse(d); img,w,h=mapframe.unpack(root.kids); P=mapframe.palette(root.kids)
        nc=mapframe.pack(root.kids,mapframe.apply(img,P),w,h); assert nc<=433,nc
        nd=cbuild(root); ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append(f'MAPFRAME cells {nc}')
# boxes in true screen pixels (cells decoded with map value n = cell n//2)
DOCK=[((13,16,58,30),'도크',12,'center'),((97,16,131,30),'자금',12,'center'),((217,16,251,30),'자원',12,'center'),
      ((90,36,136,53),'병기명',12,'center'),((150,36,178,53),'기수',12,'center'),((190,36,222,53),'자금',12,'center'),
      ((254,36,286,53),'자원',12,'center'),((304,36,338,53),'기간',12,'center'),
      ((15,87,44,102),'차량',12,'center'),((15,104,44,120),'항공',12,'center'),((15,122,44,138),'우주',12,'center'),
      ((15,141,44,156),'함선',12,'center'),((15,159,44,175),'종료',12,'center')]
def build_dock(changed,report):
    """DATA01 entry0: production-dock NBG frame (8bpp cells + 44x28 map) with baked labels"""
    import data05,retext; import numpy as np
    name='DATA01.MFD'
    if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
    ent=changed[name][0][0]
    d=ent['new_data'] if 'new_data' in ent else decode(ent)
    root=parse(d); img,w,h,mp=data05.unpack_kids(root.kids,0); P=data05.palette(root.kids[2].data)
    b=struct.pack('>HH',w*8,h*8)+img.tobytes()
    masks={}
    for box,t,sz,al in DOCK:
        kw=dict(align=al,outline=False,shrink_to_fit=True,ink='dark' if box[0]==15 else None)
        if box[0]==15:
            # text pixels of this menu row = where the label differs from the blank (erased) row
            _,blank=retext.retext(b,P,box,'','NanumSquareNeo-cBd.ttf',sz,**kw)
        b,res=retext.retext(b,P,box,t,'NanumSquareNeo-cBd.ttf',sz,**kw)
        if box[0]==15:
            Lm=P@np.array([0.3,0.59,0.11],np.float32); masks[t]=(Lm[blank]-Lm[res])>22
    # the selected row is shown by a green sprite drawn over the baked dark label: kid -> (label, screen y);
    # x=15 for all. Positions measured by matching the original sprites against the original frame.
    for k,(t,sy) in {7:('차량',88),8:('항공',104),9:('우주',120),10:('함선',136),11:('종료',160)}.items():
        kid=root.kids[k]; a=dec_lab(kid.data); sh,sw=a.shape
        m=masks[t][sy:sy+sh,15:15+sw]
        o=np.zeros_like(a)
        ring=np.zeros_like(m)
        for dy in (-1,0,1):
            for dx in (-1,0,1): ring|=np.roll(np.roll(m,dy,0),dx,1)
        o[m]=1                        # green core (palette of kid 4)
        kid.data=enc_lab(kid.data,o)
    # keep the original cell numbers: the game draws the dock no./funds into fixed cells
    nc=data05.pack_kids_keep(root.kids,res.astype('uint8'),w,h,mp,1207,base=0)
    nd=cbuild(root); ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append(f'DOCK cells {nc}')
def build_dev(changed,report):
    import data05,retext
    name='DATA05.MFD'
    if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
    ent=changed[name][0][0]
    d=ent['new_data'] if 'new_data' in ent else decode(ent)
    img,w,h,mp,pal=data05.unpack(d); P=data05.palette(pal)
    b=struct.pack('>HH',w*8,h*8)+img.tobytes()
    for box,t in (((22,7,80,19),'개발 NO.'),((22,24,80,36),'개발 예산'),((22,41,80,53),'개발 기간')):
        b,res=retext.retext(b,P,box,t,'NanumSquareNeo-cBd.ttf',12,outline=False,shrink_to_fit=False)
    nd,nc=data05.pack(res.astype('uint8'),w,h,mp,pal)
    ent['new_data']=nd; ent['new']=encode(ent,nd)
    report.append(f'DEV cells {nc}')
def build_kfont(changed,rawfiles,report):
    import kfont as KF, kfields, re
    S=json.load(open(os.path.join(W,'kfont','strings.json'),encoding='utf8'))
    allko=list(S['gdata'].values())+list(S['prog'].values())
    syl=sorted({ch for t in allko for ch in t if KF.is_hangul(ch)})
    enc=KF.Encoder(syl); bank=KF.build_bank(syl)
    pool_addr=KF.pool_base(bank); pool=bytearray(); pooled={}
    G={k.encode('cp932'):enc.enc(v) for k,v in S['gdata'].items()}
    P={k.encode('cp932'):enc.enc(v) for k,v in S['prog'].items()}
    ng=np_=nr=0
    for name in sorted(os.listdir(os.path.join(W,'disc'))):
        if not (name.startswith('GDATA') or name.startswith('PROG0')) or not name.endswith('.MFD'): continue
        if name not in changed: changed[name]=split(open(os.path.join(W,'disc',name),'rb').read())
        ents,_=changed[name]
        for ent in ents:
            data=ent['new_data'] if 'new_data' in ent else decode(ent)
            nd=bytearray(data); tot=0
            if name=='PROG00.MFD' and 'titles' in os.environ.get('PARTS','titles'):
                import progimg; nd=bytearray(progimg.patch_prog00(bytes(nd))); tot+=1
            if name.startswith('GDATA'):
                for sec,p,t in list(kfields.fields(bytes(nd),name)):
                    if t in G:
                        k=G[t]; n=max(len(t),len(k)); nd[p:p+n]=k+bytes(n-len(k)); tot+=1; ng+=1
            elif name.startswith('PROG0'):
                for m in list(re.finditer(rb'(?<=[\x00\xff])[\x20-\x7e\xa1-\xdf]{2,}(?=\x00)',bytes(nd))):
                    t=m.group()
                    if t not in P: continue
                    k=P[t]; p=m.start(); room=len(t)
                    q=p+len(t)+1
                    while q<len(nd) and nd[q]==0xff: q+=1; room+=1
                    if len(k)<=room:
                        nd[p:p+len(k)+1]=k+b'\0'; tot+=1; np_+=1
                    else:
                        hits=[]
                        for base in (0x6060000,ent.get('dest') or 0x6060000):
                            ptr=struct.pack('>I',base+p); hits=[h.start() for h in re.finditer(re.escape(ptr),bytes(nd)) if h.start()%2==0]
                            if hits: break
                        if not hits: report.append(f'KF no ptr {name} {t.decode("cp932")}'); continue
                        if k not in pooled: pooled[k]=pool_addr+len(pool); pool+=k+b'\0'; pool+=bytes(-len(pool)%2)
                        for h in hits: struct.pack_into('>I',nd,h,pooled[k])
                        tot+=1; nr+=1
            if name.startswith('PROG0') and KF.TABLE_SIG in nd: nd=bytearray(KF.patch_table(bytes(nd))); tot+=1
            if tot:
                ent['new_data']=bytes(nd); ent['new']=encode(ent,bytes(nd))
    code=open(os.path.join(W,'kfont','kfont.bin'),'rb').read(); init=open(os.path.join(W,'kfont','init.bin'),'rb').read()
    import msub
    mcode,lw=msub_parts()
    main=open(os.path.join(W,'disc','00000000.BIN'),'rb').read()
    if mcode: main=msub.patch_main(main)
    main=KF.patch_main(main,bank,code,init,bytes(pool),mcode,lw)
    report.append(f'MSUB code {len(mcode)} data {len(lw)}')
    rawfiles['00000000.BIN']=bytes(main)
    report.append(f'KF syllables {len(syl)} gdata {ng} prog {np_} relocated {nr} pool {len(pool)} payload end {KF.pool_base(bank)+len(pool):x}')
def main():
    ko=load_ko(); report=[]
    src=os.path.join(ROOT,BASE+' (Track 1).bin')
    img=Image(src); dents={e['name']:e for e in img.dir_entries()}
    parts=os.environ.get('PARTS','scenes,help,ui,names,bram,hekik,mapframe,dock,dev,g16,ending,kfont,msub').split(',')
    changed=build_scenes(ko,img,None,report) if 'scenes' in parts else {}
    if 'help' in parts: build_help(changed,report)
    if 'ui' in parts: build_ui(changed,report)
    if 'names' in parts: build_names(changed,report)
    if 'bram' in parts: build_bram(changed,report)
    if 'hekik' in parts: build_hekik(changed,report)
    if 'mapframe' in parts: build_mapframe(changed,report)
    if 'dock' in parts: build_dock(changed,report)
    rawfiles={}
    if 'dev' in parts: build_dev(changed,report)
    if 'g16' in parts: build_glyph16(changed,report)
    if 'ending' in parts: build_ending(changed,report)
    if 'kfont' in parts: build_kfont(changed,rawfiles,report)
    end=max(e['lba']+(e['size']+2047)//2048 for e in dents.values())
    end=max(end,img.nsec)
    for name,(ents,last) in sorted(changed.items()):
        raws=[e.get('new',e['raw']) for e in ents]
        blob=join(raws)
        blob+=bytes(-len(blob)%4)   # every original MFD size is a multiple of 4; the loader relies on it
        de=dents[name]; oldsec=(de['size']+2047)//2048; newsec=(len(blob)+2047)//2048
        if newsec<=oldsec: lba=de['lba']
        else: lba=end; end+=newsec
        img.write_data(lba,blob); img.set_entry(de,lba,len(blob))
        de['lba']=lba; de['size']=len(blob)
    for name,blob in sorted(rawfiles.items()):
        de=dents[name]; oldsec=(de['size']+2047)//2048; newsec=(len(blob)+2047)//2048
        if newsec<=oldsec: lba=de['lba']
        else: lba=end; end+=newsec
        img.write_data(lba,blob); img.set_entry(de,lba,len(blob))
        de['lba']=lba; de['size']=len(blob)
    out1=os.path.join(ROOT,OUTB+' (Track 1).bin')
    img.save(out1)
    t2=os.path.join(ROOT,OUTB+' (Track 2).bin')
    if not os.path.exists(t2): shutil.copyfile(os.path.join(ROOT,BASE+' (Track 2).bin'),t2)
    cue=open(os.path.join(ROOT,BASE+'.cue'),encoding='latin1').read().replace(BASE,OUTB)
    open(os.path.join(ROOT,OUTB+'.cue'),'w',encoding='latin1').write(cue)
    import mfdpack; report.append(f'LZ over {len(mfdpack.OVER)} {mfdpack.OVER[:12]}')
    print('changed files',len(changed),'end lba',end); print('\n'.join(report[:50]))
if __name__=='__main__': main()




